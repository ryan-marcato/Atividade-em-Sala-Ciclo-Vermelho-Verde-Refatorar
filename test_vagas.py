"""
PLANO (Passo 1) - Atividade Ciclo Vermelho-Verde-Refatorar
==========================================================
Problema escolhido:
    Controle de vagas de estacionamento via sensores (requisito do protótipo
    controle_vagas.py): quando o sensor detecta entrada/saída de um veículo,
    o status da vaga é atualizado e refletido no painel de controle e no log.
    (Componente reescrito do zero, guiado por testes; a leitura do sensor é
    injetada como booleano, o que torna o comportamento testável sem random.)

Casos de teste (3 variações de comportamento):
    CT1 - Entrada de veículo: vaga LIVRE -> OCUPADA, painel e log atualizados.
    CT2 - Saída de veículo:   vaga OCUPADA -> LIVRE, painel e log atualizados.
    CT3 - Leitura repetida (sem mudança): nada muda e nenhum evento é gerado.

Padrão de projeto escolhido: OBSERVER (Observador)
    Por quê: no fim da fase verde, Estacionamento atualiza status, painel e log
    diretamente (alto acoplamento). Cada vez que surgir um novo "interessado"
    na mudança de uma vaga (alarme, app, banco de dados), seria preciso alterar
    a classe. Com Observer, a Vaga (Sujeito) apenas notifica seus observadores
    (PainelDeControle, RegistroDeEventos) quando o status muda.

Tempo previsto por fase (120 min):
    10 min plano | red: 10 min | green: 10 min (commits red/green até os 25 min)
    | refactor: 50 min | autoavaliação: 10 min | folga: 30 min

"""
import pytest

from vagas import Estacionamento, StatusVaga


@pytest.fixture
def estacionamento():
    return Estacionamento(total_vagas=3)


def test_ct1_entrada_de_veiculo_ocupa_vaga_e_atualiza_painel_e_log(estacionamento):
    mudou = estacionamento.processar_leitura(numero_vaga=1, ocupada=True)

    assert mudou is True
    assert estacionamento.status_da_vaga(1) == StatusVaga.OCUPADA
    assert estacionamento.resumo_painel() == "Livres: 2 | Ocupadas: 1"
    assert estacionamento.log == ["SENSOR-01 -> vaga 01 agora está OCUPADA"]


def test_ct2_saida_de_veiculo_libera_vaga_e_atualiza_painel_e_log(estacionamento):
    estacionamento.processar_leitura(numero_vaga=2, ocupada=True)

    mudou = estacionamento.processar_leitura(numero_vaga=2, ocupada=False)

    assert mudou is True
    assert estacionamento.status_da_vaga(2) == StatusVaga.LIVRE
    assert estacionamento.resumo_painel() == "Livres: 3 | Ocupadas: 0"
    assert estacionamento.log[-1] == "SENSOR-02 -> vaga 02 agora está LIVRE"
    assert len(estacionamento.log) == 2


def test_ct3_leitura_repetida_nao_altera_estado_nem_gera_evento(estacionamento):
    mudou = estacionamento.processar_leitura(numero_vaga=3, ocupada=False)

    assert mudou is False
    assert estacionamento.status_da_vaga(3) == StatusVaga.LIVRE
    assert estacionamento.resumo_painel() == "Livres: 3 | Ocupadas: 0"
    assert estacionamento.log == []
