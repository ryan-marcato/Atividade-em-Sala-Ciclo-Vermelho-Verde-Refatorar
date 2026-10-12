"""
Controle de vagas via sensores - fase REFATORAR.

PADRÃO DE PROJETO APLICADO: OBSERVER (Observador)
Participantes, nomeados conforme o domínio:
    - Observer (interface) ........ ObservadorDeVaga
    - Subject (Sujeito) ........... Vaga   (notifica quando seu status muda)
    - ConcreteObserver A .......... PainelDeControle   (contagem livres/ocupadas)
    - ConcreteObserver B .......... RegistroDeEventos  (log das mudanças)
    - Cliente / montagem .......... Estacionamento (cria vagas e registra os
                                    observadores; recebe as leituras dos sensores)
O comportamento observável é o mesmo da fase verde (mesmos testes, sem edição).
"""
from abc import ABC, abstractmethod
from enum import Enum


class StatusVaga(Enum):
    LIVRE = "livre"
    OCUPADA = "ocupada"


class ObservadorDeVaga(ABC):
    """Observer: quem quer ser avisado quando uma vaga muda de status."""

    @abstractmethod
    def vaga_atualizada(self, vaga: "Vaga") -> None: ...


class Vaga:
    """Subject: guarda seu status e notifica os observadores ao mudar."""

    def __init__(self, numero: int):
        self.numero = numero
        self.status = StatusVaga.LIVRE
        self._observadores: list[ObservadorDeVaga] = []

    @property
    def id_sensor(self) -> str:
        return f"SENSOR-{self.numero:02d}"

    def adicionar_observador(self, observador: ObservadorDeVaga) -> None:
        self._observadores.append(observador)

    def atualizar_status(self, ocupada: bool) -> bool:
        novo = StatusVaga.OCUPADA if ocupada else StatusVaga.LIVRE
        if novo == self.status:
            return False
        self.status = novo
        for observador in self._observadores:
            observador.vaga_atualizada(self)
        return True


class PainelDeControle(ObservadorDeVaga):
    """ConcreteObserver: mantém a contagem exibida no painel."""

    def __init__(self, total_vagas: int):
        self._total = total_vagas
        self._ocupadas: set[int] = set()

    def vaga_atualizada(self, vaga: Vaga) -> None:
        if vaga.status == StatusVaga.OCUPADA:
            self._ocupadas.add(vaga.numero)
        else:
            self._ocupadas.discard(vaga.numero)

    def resumo(self) -> str:
        ocupadas = len(self._ocupadas)
        return f"Livres: {self._total - ocupadas} | Ocupadas: {ocupadas}"


class RegistroDeEventos(ObservadorDeVaga):
    """ConcreteObserver: registra cada mudança de status."""

    def __init__(self):
        self.eventos: list[str] = []

    def vaga_atualizada(self, vaga: Vaga) -> None:
        self.eventos.append(
            f"{vaga.id_sensor} -> vaga {vaga.numero:02d} "
            f"agora está {vaga.status.value.upper()}"
        )


class Estacionamento:
    def __init__(self, total_vagas: int):
        self._vagas = {n: Vaga(n) for n in range(1, total_vagas + 1)}
        self._painel = PainelDeControle(total_vagas)
        self._registro = RegistroDeEventos()
        for vaga in self._vagas.values():
            vaga.adicionar_observador(self._painel)
            vaga.adicionar_observador(self._registro)

    @property
    def log(self) -> list[str]:
        return self._registro.eventos

    def status_da_vaga(self, numero: int) -> StatusVaga:
        return self._vagas[numero].status

    def processar_leitura(self, numero_vaga: int, ocupada: bool) -> bool:
        return self._vagas[numero_vaga].atualizar_status(ocupada)

    def resumo_painel(self) -> str:
        return self._painel.resumo()



# AUTOAVALIAÇÃO (Passo 3)
# Critérios atingidos (conferidos com a execução final, ver saida_testes.txt):
#  1. Testes em arquivo separado (test_vagas.py), 1 teste por variação (CT1-CT3): SIM
#  2. Três commits, um por fase, com red/green/refactor na mensagem: SIM
#  3. Commit red contém só os testes (vagas.py não existia): SIM
#  4. Padrão Observer nomeado em comentário, participantes conforme o domínio: SIM
#  5. Suíte executada após a refatoração, 3 passed, saída em saida_testes.txt: SIM
# Critérios não atingidos: nenhum. Observação: o tempo por fase não foi
# cronometrado de forma rigorosa (preencher com os tempos reais).
#
# O que mudou entre verde e refatorado: na verde, Estacionamento guardava os
# status num dicionário e, ao mudar, atualizava log e painel por conta própria.
# Na refatorada, a mudança de status vive em Vaga (Subject), que notifica
# PainelDeControle e RegistroDeEventos (Observers). Para ter um novo interessado
# (ex.: alarme) basta criar outro observador, sem editar Estacionamento. Os
# testes não precisaram de nenhuma alteração.
#
# Parte que deu mais trabalho: fazer o painel acompanhar o estado só por
# notificações (contagem inicial correta e sem duplicar) e escolher a API
# pública mantida (processar_leitura, resumo_painel, log) para os testes
# continuarem válidos sem edição.

