import { z } from 'zod'

// Schema para validação de cliente
export const schemaCliente = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  telefone: z.string().optional(),
  tipo_cliente: z.enum(['residencial', 'comercial'], {
    message: 'Tipo de cliente inválido'
  })
})

// Schema para validação de transação
export const schemaTransacao = z.object({
  descricao: z.string().min(3, 'Descrição deve ter pelo menos 3 caracteres'),
  valor: z.number().positive('Valor deve ser maior que zero'),
  tipo: z.enum(['receita', 'despesa'], {
    message: 'Tipo de transação inválido'
  }),
  categoria_id: z.string().min(1, 'Categoria é obrigatória'),
  data_vencimento: z.string().min(1, 'Data de vencimento é obrigatória')
})

// Schema para validação de ordem de serviço
export const schemaOrdemServico = z.object({
  titulo: z.string().min(3, 'Título deve ter pelo menos 3 caracteres'),
  cliente_id: z.string().min(1, 'Cliente é obrigatório'),
  tipo_servico_id: z.string().min(1, 'Tipo de serviço é obrigatório'),
  descricao: z.string().min(10, 'Descrição deve ter pelo menos 10 caracteres'),
  status: z.enum(['pendente', 'em_andamento', 'concluida', 'cancelada'], {
    message: 'Status inválido'
  }),
  prioridade: z.enum(['baixa', 'normal', 'alta', 'urgente'], {
    message: 'Prioridade inválida'
  })
})

// Schema para validação de orçamento
export const schemaOrcamento = z.object({
  titulo: z.string().min(3, 'Título deve ter pelo menos 3 caracteres'),
  cliente_id: z.string().min(1, 'Cliente é obrigatório'),
  descricao: z.string().min(3, 'Descrição deve ter pelo menos 3 caracteres'),
  tipo_calculo: z.enum(['automatico', 'manual'], {
    message: 'Tipo de cálculo inválido'
  }),
  valido_ate: z.string().optional().refine((val) => {
    if (!val || val === '') return true
    const data = new Date(val)
    const hoje = new Date()
    hoje.setHours(0, 0, 0, 0)
    return data >= hoje
  }, 'Válido até não pode ser uma data no passado'),
  condicoes_pagamento: z.string().optional(),
  garantia: z.string().optional(),
  observacoes_internas: z.string().optional(),
  tipo_desconto: z.enum(['', 'valor', 'percentual'], {
    message: 'Tipo de desconto inválido'
  }),
  valor_desconto: z.number().min(0, 'Valor do desconto não pode ser negativo').optional(),
  taxa_imposto: z.number().min(0, 'Taxa de imposto não pode ser negativa').optional(),
  valor_total_manual: z.number().positive('Valor total manual deve ser maior que zero').optional()
})

// Schema para validação de item de estoque
export const schemaEstoqueItem = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  sku: z.string().min(1, 'SKU é obrigatório'),
  descricao: z.string().optional(),
  categoria_id: z.string().min(1, 'Categoria é obrigatória'),
  custo_unitario: z.number().positive('Custo unitário deve ser maior que zero'),
  preco_venda: z.number().positive('Preço de venda deve ser maior que zero'),
  estoque_atual: z.number().min(0, 'Estoque atual não pode ser negativo'),
  estoque_minimo: z.number().min(0, 'Estoque mínimo não pode ser negativo')
})

// Tipos inferidos dos schemas
export type ClienteFormData = z.infer<typeof schemaCliente>
export type TransacaoFormData = z.infer<typeof schemaTransacao>
export type OrdemServicoFormData = z.infer<typeof schemaOrdemServico>
export type OrcamentoFormData = z.infer<typeof schemaOrcamento>
export type EstoqueItemFormData = z.infer<typeof schemaEstoqueItem>
