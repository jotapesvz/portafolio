"""
Nauvo Risk Engine - Interactive Prototype (TRL 4 Demo)
Autor: Juan Pablo Silva (Product Manager & Co-Founder)

Demostración del motor de inferencia determinista sobre Grafo Dirigido Acíclico (DAG)
para evaluación de riesgo de inversión en startups tempranas.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class StartupInput:
    name: str
    stage: str
    founder_experience_score: float  # 0.0 a 1.0
    complementary_team: float        # 0.0 a 1.0 (roles técnicos y de negocio cubiertos)
    tam_sam_clarity: float           # 0.0 a 1.0 (evidencia de mercado)
    competitive_moat: float          # 0.0 a 1.0 (barreras de entrada / IP)
    traction_evidence: float         # 0.0 a 1.0 (MRR, cartas de intención, pilotos)
    runway_months: int               # meses de caja disponibles


class NauvoDAGInferenceEngine:
    """
    Motor determinista que propaga puntuaciones empíricas sobre nodos de un DAG.
    Garantiza parsimonia, explicabilidad matemática y cero alucinaciones en el cálculo.
    """

    def __init__(self):
        # Ponderaciones empíricas estáticas basadas en tesis de magíster
        self.weights_execution = {
            "founder_experience": 0.55,
            "complementary_team": 0.45,
        }
        self.weights_market = {
            "tam_sam_clarity": 0.50,
            "competitive_moat": 0.50,
        }
        self.weights_financial = {
            "traction": 0.60,
            "runway": 0.40,
        }

    def _normalize_runway(self, months: int) -> float:
        """Normaliza el runway en un score de 0.0 a 1.0 (18+ meses = 1.0, <3 meses = 0.0)"""
        if months >= 18:
            return 1.0
        if months <= 3:
            return 0.1
        return round((months - 3) / 15.0, 2)

    def evaluate(self, data: StartupInput) -> Dict:
        # 1. Nodos de Nivel 1 (Sub-dimensiones)
        runway_score = self._normalize_runway(data.runway_months)

        # 2. Nodos de Nivel 2 (Dimensiones Macro)
        team_strength = (
            data.founder_experience_score * self.weights_execution["founder_experience"] +
            data.complementary_team * self.weights_execution["complementary_team"]
        )
        market_viability = (
            data.tam_sam_clarity * self.weights_market["tam_sam_clarity"] +
            data.competitive_moat * self.weights_market["competitive_moat"]
        )
        traction_financial = (
            data.traction_evidence * self.weights_financial["traction"] +
            runway_score * self.weights_financial["runway"]
        )

        # 3. Cálculo de Riesgo Inverso (1.0 = Muy Fuerte / Menor Riesgo)
        # Índice Compuesto de Riesgo (Escala 0 a 100, donde 100 es Riesgo Máximo y 0 es Riesgo Nulo)
        composite_strength = (team_strength * 0.40) + (market_viability * 0.35) + (traction_financial * 0.25)
        risk_score = round((1.0 - composite_strength) * 100, 1)

        # 4. Auditoría de Cuellos de Botella (Alertas de Inversión)
        bottlenecks: List[str] = []
        if team_strength < 0.5:
            bottlenecks.append("ALERTA CRÍTICA: Desbalance en equipo fundador o falta de experiencia de dominio.")
        if market_viability < 0.4:
            bottlenecks.append("ALERTA DE MERCADO: Barreras de entrada bajas o falta de claridad en tamaño de mercado (SAM).")
        if data.runway_months < 6:
            bottlenecks.append(f"ALERTA DE LIQUIDEZ: Runway urgente ({data.runway_months} meses). Requiere ronda inmediata.")
        if data.traction_evidence < 0.3:
            bottlenecks.append("ALERTA DE TRACCIÓN: Validación comercial insuficiente para la etapa declarada.")

        # Recomendación del Comité
        if risk_score <= 30.0:
            recommendation = "BAJO RIESGO RELATIVO — Recomendado para Due Diligence profundo"
        elif risk_score <= 55.0:
            recommendation = "RIESGO MODERADO — Requiere mitigar cuellos de botella específicos"
        else:
            recommendation = "ALTO RIESGO — Fuera de tesis estándar de inversión en pre-seed"

        return {
            "startup_name": data.name,
            "stage": data.stage,
            "risk_score_100": risk_score,
            "dimensions": {
                "Equipo y Ejecución": round(team_strength * 100, 1),
                "Mercado y Defendibilidad": round(market_viability * 100, 1),
                "Tracción y Runway": round(traction_financial * 100, 1),
            },
            "bottlenecks": bottlenecks,
            "recommendation": recommendation,
        }


def print_report(result: Dict):
    print("\n" + "=" * 65)
    print(f"  NAUVO INFERENCE ENGINE — AUDIT REPORT: {result['startup_name'].upper()}")
    print("=" * 65)
    print(f"Etapa declarada: {result['stage']}")
    print(f"Índice Compuesto de Riesgo (0-100): {result['risk_score_100']} / 100")
    print(f"Dictamen: {result['recommendation']}")
    print("-" * 65)
    print("DESGLOSE POR DIMENSIÓN DEL GRAFO (Fuerza 0-100%):")
    for dim, score in result["dimensions"].items():
        bar = "█" * int(score // 5) + "░" * (20 - int(score // 5))
        print(f"  • {dim:<25} : {score:>5.1f}% [{bar}]")
    print("-" * 65)
    print("CUELLOS DE BOTELLA IDENTIFICADOS (TRAZABILIDAD EXPLICABLE):")
    if result["bottlenecks"]:
        for b in result["bottlenecks"]:
            print(f"  ⚠️  {b}")
    else:
        print("  ✅ No se detectaron anomalías críticas en el grafo.")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    engine = NauvoDAGInferenceEngine()

    # Caso de prueba 1: Startup con fuerte equipo y tracción pero bajo runway
    sample_startup = StartupInput(
        name="FinTrack AI",
        stage="Seed",
        founder_experience_score=0.85,
        complementary_team=0.90,
        tam_sam_clarity=0.75,
        competitive_moat=0.70,
        traction_evidence=0.80,
        runway_months=4,
    )

    result = engine.evaluate(sample_startup)
    print_report(result)
