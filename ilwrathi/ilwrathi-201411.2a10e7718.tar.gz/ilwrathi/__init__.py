#!/usr/bin/env python
"""Ilwrath is a framwork for building web pen testing tools.

Ilwrath currently contains Sac. Sac is a base class that can be
extended to handle performing operations that have multiple
dependances. This was created to solve the problem of testing web
services with multiple dependances."""

from .iac import IdempotentAccessor

__all__ = ["IdempotentAccessor", "clients"]
