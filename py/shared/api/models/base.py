from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class R2RResults(BaseModel, Generic[T]):
    results: T


class PaginatedR2RResult(BaseModel, Generic[T]):
    results: T
    total_entries: int

    # Convenience: act like the underlying list when appropriate
    def __len__(self):  # type: ignore[override]
        try:
            return len(self.results)  # type: ignore[arg-type]
        except Exception:
            return 0

    def __iter__(self):  # type: ignore[override]
        try:
            return iter(self.results)  # type: ignore[arg-type]
        except Exception:
            return iter(())

    def __getitem__(self, index):  # type: ignore[override]
        try:
            return self.results[index]  # type: ignore[index]
        except Exception as e:
            raise TypeError("Results object is not indexable") from e


class GenericBooleanResponse(BaseModel):
    success: bool


class GenericMessageResponse(BaseModel):
    message: str


WrappedBooleanResponse = R2RResults[GenericBooleanResponse]
WrappedGenericMessageResponse = R2RResults[GenericMessageResponse]
