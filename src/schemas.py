"""Pydantic models for the LLM extraction of one earnings release."""

from typing import Literal

from pydantic import BaseModel, Field


class Quote(BaseModel):
    page: int  # 1-based
    text: str


class GuidanceItem(BaseModel):
    metric: str
    period: str
    perimeter: str | None
    low: float | None
    high: float | None
    unit: str
    assumptions: str | None
    statement: str
    quote: Quote
    verified: bool | None = None
    issues: list[str] = Field(default_factory=list)


class ToneSignal(BaseModel):
    dimension: Literal[
        "demand_prices",
        "costs_margins",
        "operations_execution",
        "macro_regulation",
        "cash_balance_sheet",
    ]
    direction: Literal["positive", "neutral", "negative"]
    horizon: Literal["forward", "backward"]
    quote: Quote
    verified: bool | None = None
    issues: list[str] = Field(default_factory=list)


class Theme(BaseModel):
    name: str
    summary: str
    keywords: list[str]
    quotes: list[Quote]
    verified: bool | None = None
    issues: list[str] = Field(default_factory=list)


class CapitalAllocationItem(BaseModel):
    category: Literal[
        "M&A",
        "divestment",
        "debt_issuance",
        "equity_issuance",
        "buyback",
        "dividends",
        "leverage",
        "capex",
    ]
    summary: str
    quote: Quote
    verified: bool | None = None
    issues: list[str] = Field(default_factory=list)


class ReleaseExtraction(BaseModel):
    company: str
    period: str
    guidance: list[GuidanceItem]
    tone_signals: list[ToneSignal]
    themes: list[Theme]
    capital_allocation: list[CapitalAllocationItem]
