import { describe, it, expect } from 'vitest'
import { schemaCliente, schemaTransacao, schemaEstoqueItem, schemaOrcamento } from '@/lib/validacoes'

describe('schemaCliente', () => {
  it('email inválido deve falhar', () => {
    const result = schemaCliente.safeParse({
      nome: 'João Silva',
      email: 'email-invalido',
      tipo_cliente: 'residencial'
    })
    expect(result.success).toBe(false)
  })

  it('campos obrigatórios vazios devem falhar', () => {
    const result = schemaCliente.safeParse({
      nome: '',
      email: '',
      tipo_cliente: 'residencial'
    })
    expect(result.success).toBe(false)
  })

  it('dados válidos devem passar', () => {
    const result = schemaCliente.safeParse({
      nome: 'João Silva',
      email: 'joao@example.com',
      tipo_cliente: 'residencial'
    })
    expect(result.success).toBe(true)
  })
})

describe('schemaTransacao', () => {
  it('valor negativo deve falhar', () => {
    const result = schemaTransacao.safeParse({
      descricao: 'Teste',
      valor: -10,
      tipo: 'receita',
      categoria_id: '1',
      data_vencimento: '2024-01-01'
    })
    expect(result.success).toBe(false)
  })

  it('tipo inválido deve falhar', () => {
    const result = schemaTransacao.safeParse({
      descricao: 'Teste',
      valor: 100,
      tipo: 'invalido' as any,
      categoria_id: '1',
      data_vencimento: '2024-01-01'
    })
    expect(result.success).toBe(false)
  })
})

describe('schemaEstoqueItem', () => {
  it('estoque negativo deve falhar', () => {
    const result = schemaEstoqueItem.safeParse({
      nome: 'Item Teste',
      sku: 'SKU001',
      categoria_id: '1',
      custo_unitario: 10,
      preco_venda: 20,
      estoque_atual: -5,
      estoque_minimo: 0
    })
    expect(result.success).toBe(false)
  })
})

describe('schemaOrcamento', () => {
  it('valido_ate no passado deve falhar', () => {
    const dataPassada = new Date()
    dataPassada.setFullYear(dataPassada.getFullYear() - 1)
    const dataPassadaStr = dataPassada.toISOString().split('T')[0]
    
    const result = schemaOrcamento.safeParse({
      titulo: 'Orçamento Teste',
      cliente_id: '1',
      descricao: 'Descrição teste',
      tipo_calculo: 'automatico',
      valido_ate: dataPassadaStr
    })
    expect(result.success).toBe(false)
  })
})
