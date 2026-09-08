#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repositorio para buttons.json"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class ButtonRepository:
    """Carga y consulta configuración de botones"""
    
    def __init__(self, config_path: str = "buttons.json"):
        self.config_path = Path(config_path)
        self._buttons = None
        self._buttons_by_label = {}
        self._load()
    
    def _load(self):
        """Carga el archivo JSON"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"No se encuentra: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._buttons = json.load(f)
        
        # Indexar por label para búsqueda rápida
        self._buttons_by_label = {
            b['label']: b for b in self._buttons
        }
    
    def get_all(self) -> List[Dict]:
        """Obtiene todos los botones"""
        return self._buttons
    
    def get_by_label(self, label: str) -> Optional[Dict]:
        """Obtiene un botón por su label"""
        return self._buttons_by_label.get(label)
    
    def get_test_names(self) -> List[str]:
        """Obtiene todos los nombres de pruebas"""
        return list(self._buttons_by_label.keys())
    
    def get_sequence_buttons(self, sequence_name: str) -> List[Dict]:
        """Obtiene los botones de una secuencia"""
        button = self.get_by_label(sequence_name)
        if not button:
            return []
        
        action = button.get('action', {})
        if action.get('type') != 'sequence_buttons':
            return []
        
        button_names = action.get('buttons', [])
        return [self.get_by_label(name) for name in button_names if self.get_by_label(name)]
    
    def reload(self):
        """Recarga el archivo"""
        self._buttons = None
        self._buttons_by_label = {}
        self._load()