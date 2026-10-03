"""HTTP client with bounded retries and response validation."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests

logger = logging.getLogger(__name__)


class DatajudError(RuntimeError):
    """Base error for a failed Datajud request."""


class AuthenticationError(DatajudError):
    """The API rejected the credential."""


class RateLimitError(DatajudError):
    """The API kept returning HTTP 429 after retries."""


class TransientDatajudError(DatajudError):
    """A bounded retryable failure exhausted its attempts."""


class InvalidResponseError(DatajudError):
    """A successful HTTP response does not match the expected contract."""


@dataclass(frozen=True)
class SearchPage:
    raw: dict[str, Any]
    hits: tuple[dict[str, Any], ...]
    next_cursor: list[Any] | None
    total: dict[str, Any]


class DatajudClient:
    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        connect_timeout_seconds: float,
        read_timeout_seconds: float,
        max_attempts: int,
        max_wait_seconds: float,
        sleep: Callable[[float], None] = time.sleep,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key.strip():
            raise AuthenticationError("DATAJUD_API_KEY não foi informado")
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = (connect_timeout_seconds, read_timeout_seconds)
        self.max_attempts = max_attempts
        self.max_wait_seconds = max_wait_seconds
        self.sleep = sleep
        self.session = session or requests.Session()
        self.last_request_meta: dict[str, Any] = {}

    def search(self, body: dict[str, Any]) -> SearchPage:
        headers = {
            "Authorization": f"APIKey {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.session.post(
                    self.endpoint,
                    headers=headers,
                    json=body,
                    timeout=self.timeout,
                )
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_error = exc
                if attempt == self.max_attempts:
                    raise TransientDatajudError("falha transitória após tentativas limitadas") from exc
                wait = self._backoff(attempt)
                logger.warning("falha de conexão (%s); nova tentativa em %.0fs", type(exc).__name__, wait)
                self.sleep(wait)
                continue

            if response.status_code in (401, 403):
                self.last_request_meta = {"attempts": attempt, "status_code": response.status_code}
                raise AuthenticationError(f"Datajud recusou a autenticação (HTTP {response.status_code})")
            if response.status_code == 429:
                if attempt == self.max_attempts:
                    self.last_request_meta = {"attempts": attempt, "status_code": 429}
                    raise RateLimitError("Datajud manteve HTTP 429 após tentativas limitadas")
                wait = self._retry_after(response, attempt)
                logger.warning("HTTP 429; nova tentativa em %.0fs", wait)
                self.sleep(wait)
                continue
            if response.status_code in (502, 503, 504):
                if attempt == self.max_attempts:
                    self.last_request_meta = {"attempts": attempt, "status_code": response.status_code}
                    raise TransientDatajudError(
                        f"falha transitória do Datajud (HTTP {response.status_code})"
                    )
                wait = self._backoff(attempt)
                logger.warning("HTTP %d; nova tentativa em %.0fs", response.status_code, wait)
                self.sleep(wait)
                continue
            if response.status_code != 200:
                self.last_request_meta = {"attempts": attempt, "status_code": response.status_code}
                raise DatajudError(f"Datajud retornou HTTP {response.status_code}")

            self.last_request_meta = {"attempts": attempt, "status_code": response.status_code}
            return self._parse_page(response)

        raise TransientDatajudError("requisição não concluída") from last_error

    def _parse_page(self, response: requests.Response) -> SearchPage:
        try:
            raw = response.json()
        except ValueError as exc:
            raise InvalidResponseError("resposta 200 não é JSON válido") from exc
        if not isinstance(raw, dict):
            raise InvalidResponseError("resposta JSON deve ser um objeto")
        if not isinstance(raw.get("timed_out"), bool) or raw["timed_out"] is True:
            raise InvalidResponseError("resposta indicou timed_out")
        shards = raw.get("_shards")
        if (
            not isinstance(shards, dict)
            or not isinstance(shards.get("failed"), int)
            or not isinstance(shards.get("total"), int)
            or not isinstance(shards.get("successful"), int)
            or shards["failed"] > 0
        ):
            raise InvalidResponseError("resposta indicou falha de shard")
        hits_obj = raw.get("hits")
        if not isinstance(hits_obj, dict):
            raise InvalidResponseError("resposta sem objeto hits")
        hits = hits_obj.get("hits")
        total = hits_obj.get("total")
        if not isinstance(hits, list) or not isinstance(total, dict):
            raise InvalidResponseError("resposta sem hits.hits ou hits.total")
        if (
            not isinstance(total.get("value"), int)
            or total.get("value") < 0
            or total.get("relation") not in {"eq", "gte"}
        ):
            raise InvalidResponseError("hits.total inválido")
        for hit in hits:
            if not isinstance(hit, dict) or not isinstance(hit.get("_source"), dict):
                raise InvalidResponseError("hit sem _source objeto")
            if not isinstance(hit.get("sort"), list) or not hit["sort"]:
                raise InvalidResponseError("hit sem sort para paginação estável")
        cursor = list(hits[-1]["sort"]) if hits else None
        return SearchPage(raw=raw, hits=tuple(hits), next_cursor=cursor, total=total)

    def _backoff(self, attempt: int) -> float:
        return min(self.max_wait_seconds, float(2 ** (attempt - 1)))

    def _retry_after(self, response: requests.Response, attempt: int) -> float:
        try:
            value = float(response.headers.get("Retry-After", ""))
        except ValueError:
            value = self._backoff(attempt)
        return min(self.max_wait_seconds, max(0.0, value))
