"""
Módulo de Pipeline Event-Driven para Mini CRM.

Este módulo contém toda a lógica de negócio do pipeline de vendas,
completamente isolado do Django e das views.
"""

from .resolver import resolve_next_stage, checklist_completo

__all__ = ['resolve_next_stage', 'checklist_completo']
