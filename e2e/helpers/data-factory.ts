/**
 * Data Factory para gerar dados de teste consistentes
 */

export class DataFactory {
  static gerarCliente(overrides?: Partial<{ nome: string; email: string; telefone: string; endereco: string }>) {
    const timestamp = Date.now();
    return {
      nome: overrides?.nome || `Cliente Teste ${timestamp}`,
      email: overrides?.email || `cliente${timestamp}@teste.com`,
      telefone: overrides?.telefone || '(11) 99999-9999',
      endereco: overrides?.endereco || 'Rua Teste, 123 - São Paulo, SP',
    };
  }

  static gerarOrdemServico(overrides?: Partial<{ titulo: string; descricao: string; clienteId: string; categoriaId: string; prioridade: string }>) {
    const timestamp = Date.now();
    return {
      titulo: overrides?.titulo || `OS Teste ${timestamp}`,
      descricao: overrides?.descricao || 'Descrição da ordem de serviço de teste',
      clienteId: overrides?.clienteId,
      categoriaId: overrides?.categoriaId,
      prioridade: overrides?.prioridade,
    };
  }

  static gerarOrcamento(overrides?: Partial<{ clienteId: string; descricao: string; itens: Array<{ descricao: string; quantidade: number; valorUnitario: number }> }>) {
    const timestamp = Date.now();
    return {
      clienteId: overrides?.clienteId,
      descricao: overrides?.descricao || `Orçamento Teste ${timestamp}`,
      itens: overrides?.itens || [
        { descricao: 'Serviço de teste', quantidade: 1, valorUnitario: 100 },
      ],
    };
  }

  static gerarItemOrcamento(overrides?: Partial<{ descricao: string; quantidade: number; valorUnitario: number }>) {
    const timestamp = Date.now();
    return {
      descricao: overrides?.descricao || `Item ${timestamp}`,
      quantidade: overrides?.quantidade || 1,
      valorUnitario: overrides?.valorUnitario || 100,
    };
  }

  static gerarCategoriaServico(overrides?: Partial<{ nome: string; descricao: string }>) {
    const timestamp = Date.now();
    return {
      nome: overrides?.nome || `Categoria ${timestamp}`,
      descricao: overrides?.descricao || 'Categoria de serviço de teste',
    };
  }
}
