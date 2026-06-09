# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: agenda.spec.ts >> Módulo Agenda - CRUD de Eventos >> deve selecionar tipo de evento
- Location: specs\agenda.spec.ts:130:7

# Error details

```
Test timeout of 60000ms exceeded.
```

```
Error: page.click: Test timeout of 60000ms exceeded.
Call log:
  - waiting for locator('text=Reunião')
    - locator resolved to <option value="reuniao">Reunião</option>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
      - waiting 100ms
    112 × waiting for element to be visible, enabled and stable
        - element is not visible
      - retrying click action
        - waiting 500ms

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e7]:
          - img [ref=e9]
          - heading "Assistência Impacto" [level=1] [ref=e12]
          - button [ref=e13] [cursor=pointer]:
            - img [ref=e14]
        - navigation [ref=e17]:
          - generic [ref=e18]:
            - paragraph [ref=e19]: VISÃO GERAL
            - link "Dashboard" [ref=e21] [cursor=pointer]:
              - /url: /
              - img [ref=e22]
              - generic [ref=e27]: Dashboard
          - generic [ref=e28]:
            - paragraph [ref=e29]: OPERAÇÕES
            - generic [ref=e30]:
              - link "Ordens de Serviço" [ref=e31] [cursor=pointer]:
                - /url: /ordens-servico
                - img [ref=e32]
                - generic [ref=e35]: Ordens de Serviço
              - link "Orçamentos" [ref=e36] [cursor=pointer]:
                - /url: /orcamentos
                - img [ref=e37]
                - generic [ref=e40]: Orçamentos
              - link "Agenda" [ref=e41] [cursor=pointer]:
                - /url: /agenda
                - img [ref=e42]
                - generic [ref=e44]: Agenda
              - link "Clientes" [ref=e45] [cursor=pointer]:
                - /url: /clientes
                - img [ref=e46]
                - generic [ref=e51]: Clientes
          - generic [ref=e52]:
            - paragraph [ref=e53]: FINANCEIRO
            - generic [ref=e54]:
              - link "Visão Financeira" [ref=e55] [cursor=pointer]:
                - /url: /financeiro
                - img [ref=e56]
                - generic [ref=e58]: Visão Financeira
              - link "Transações" [ref=e59] [cursor=pointer]:
                - /url: /transacoes
                - img [ref=e60]
                - generic [ref=e63]: Transações
          - generic [ref=e64]:
            - paragraph [ref=e65]: RECURSOS
            - generic [ref=e66]:
              - link "Estoque" [ref=e67] [cursor=pointer]:
                - /url: /estoque
                - img [ref=e68]
                - generic [ref=e72]: Estoque
              - link "Equipe" [ref=e73] [cursor=pointer]:
                - /url: /equipe
                - img [ref=e74]
                - generic [ref=e79]: Equipe
          - generic [ref=e80]:
            - paragraph [ref=e81]: ANÁLISE
            - link "Relatórios" [ref=e83] [cursor=pointer]:
              - /url: /relatorios
              - img [ref=e84]
              - generic [ref=e86]: Relatórios
          - generic [ref=e87]:
            - paragraph [ref=e88]: SISTEMA
            - link "Configurações" [ref=e90] [cursor=pointer]:
              - /url: /configuracoes
              - img [ref=e91]
              - generic [ref=e94]: Configurações
        - generic [ref=e95]:
          - generic [ref=e96]:
            - generic [ref=e98]: A
            - generic [ref=e99]:
              - paragraph [ref=e100]: Administrador
              - paragraph [ref=e101]: admin@assistenciaimpacto.com.br
          - button "Sair" [ref=e102] [cursor=pointer]:
            - img [ref=e103]
            - generic [ref=e106]: Sair
    - generic [ref=e107]:
      - banner [ref=e108]:
        - generic [ref=e110]:
          - img [ref=e111]
          - textbox "Buscar... (Cmd+K)" [ref=e114]
        - generic [ref=e115]:
          - button [ref=e117] [cursor=pointer]:
            - img [ref=e118]
          - button "Administrador" [ref=e123] [cursor=pointer]:
            - img [ref=e125]
            - generic [ref=e128]:
              - paragraph [ref=e129]: Administrador
              - img [ref=e130]
      - main [ref=e132]:
        - generic [ref=e134]:
          - generic [ref=e135]:
            - generic [ref=e137]:
              - img [ref=e138]
              - combobox [ref=e140]:
                - option "Todos os técnicos" [selected]
                - option "João Silva"
            - button "Novo Evento" [ref=e141] [cursor=pointer]:
              - img [ref=e142]
              - text: Novo Evento
          - generic [ref=e145]:
            - img [ref=e146]
            - paragraph [ref=e148]: Nenhum evento agendado
            - paragraph [ref=e149]: Clique em "Novo Evento" para criar um
          - generic [ref=e152]:
            - generic [ref=e153]:
              - heading "Novo Evento" [level=2] [ref=e154]
              - button [ref=e155] [cursor=pointer]:
                - img [ref=e156]
            - generic [ref=e159]:
              - generic [ref=e160]:
                - generic [ref=e161]: Título *
                - textbox "Título *" [ref=e162]:
                  - /placeholder: Título do evento
              - generic [ref=e163]:
                - generic [ref=e164]:
                  - generic [ref=e165]: Técnico *
                  - combobox "Técnico *" [ref=e166]:
                    - option "Selecione um técnico" [selected]
                    - option "João Silva"
                - generic [ref=e167]:
                  - generic [ref=e168]: Cliente
                  - combobox "Cliente" [ref=e169]:
                    - option "Selecione um cliente (opcional)" [selected]
              - generic [ref=e170]:
                - generic [ref=e171]:
                  - generic [ref=e172]: Data/Hora Início *
                  - textbox "Data/Hora Início *" [ref=e173]
                - generic [ref=e174]:
                  - generic [ref=e175]: Data/Hora Fim *
                  - textbox "Data/Hora Fim *" [ref=e176]
              - generic [ref=e177]:
                - generic [ref=e178]:
                  - generic [ref=e179]: Tipo de Evento
                  - combobox "Tipo de Evento" [active] [ref=e180]:
                    - option "Serviço" [selected]
                    - option "Reunião"
                    - option "Manutenção"
                    - option "Indisponível"
                    - option "Outro"
                - generic [ref=e181]:
                  - generic [ref=e182]: Cor
                  - generic [ref=e183]:
                    - textbox "Cor" [ref=e184] [cursor=pointer]: "#3b82f6"
                    - generic [ref=e185]: "#3b82f6"
              - generic [ref=e186]:
                - generic [ref=e187]: Endereço
                - textbox "Endereço" [ref=e188]:
                  - /placeholder: Endereço do evento
              - generic [ref=e189]:
                - generic [ref=e190]: Observações
                - textbox "Observações" [ref=e191]:
                  - /placeholder: Observações adicionais
            - generic [ref=e192]:
              - button "Cancelar" [ref=e193] [cursor=pointer]
              - button "Salvar" [ref=e194] [cursor=pointer]:
                - img [ref=e195]
                - text: Salvar
  - region "Notifications alt+T"
```

# Test source

```ts
  35  |     const filtro = page.locator('[data-testid="filtro-tecnico"]');
  36  |     const valor = await filtro.inputValue();
  37  |     expect(valor).toBe('');
  38  |   });
  39  | });
  40  | 
  41  | test.describe('Módulo Agenda - CRUD de Eventos', () => {
  42  | 
  43  |   test.beforeEach(async ({ page }) => {
  44  |     await page.goto('/agenda');
  45  |     await page.waitForSelector('[data-testid="agenda-container"]');
  46  |   });
  47  | 
  48  |   test('deve abrir formulário ao clicar em Novo Evento', async ({ page }) => {
  49  |     await page.click('[data-testid="btn-novo-evento"]');
  50  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  51  |   });
  52  | 
  53  |   test('deve preencher e salvar novo evento', async ({ page }) => {
  54  |     await page.click('[data-testid="btn-novo-evento"]');
  55  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  56  | 
  57  |     // Preencher título
  58  |     await page.fill('[data-testid="input-titulo-evento"]', 'Evento de teste E2E');
  59  | 
  60  |     // Selecionar técnico
  61  |     await page.click('[data-testid="select-tecnico-evento"]');
  62  |     await page.waitForTimeout(500);
  63  |     const tecnicoOption = await page.locator('[data-testid="select-tecnico-evento"] option').nth(1);
  64  |     if (await tecnicoOption.count() > 0) {
  65  |       await page.selectOption('[data-testid="select-tecnico-evento"]', await tecnicoOption.getAttribute('value'));
  66  |     }
  67  | 
  68  |     // Preencher datas
  69  |     const dataInicio = new Date();
  70  |     dataInicio.setDate(dataInicio.getDate() + 1);
  71  |     dataInicio.setHours(10, 0, 0, 0);
  72  |     const dataInicioFormatada = new Date(dataInicio.getTime() - (dataInicio.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
  73  | 
  74  |     const dataFim = new Date(dataInicio);
  75  |     dataFim.setHours(12, 0, 0, 0);
  76  |     const dataFimFormatada = new Date(dataFim.getTime() - (dataFim.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
  77  | 
  78  |     await page.fill('[data-testid="input-data-inicio-modal"]', dataInicioFormatada);
  79  |     await page.fill('[data-testid="input-data-fim-modal"]', dataFimFormatada);
  80  | 
  81  |     // Salvar
  82  |     await page.click('[data-testid="btn-salvar-evento"]');
  83  |     
  84  |     // Modal deve fechar
  85  |     await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  86  |     await page.waitForTimeout(1000);
  87  |   });
  88  | 
  89  |   test('deve cancelar criação de evento', async ({ page }) => {
  90  |     await page.click('[data-testid="btn-novo-evento"]');
  91  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  92  | 
  93  |     await page.click('[data-testid="btn-fechar-modal"]');
  94  |     await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  95  |   });
  96  | 
  97  |   test('deve validar campos obrigatórios ao criar evento', async ({ page }) => {
  98  |     await page.click('[data-testid="btn-novo-evento"]');
  99  |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  100 | 
  101 |     // Tentar salvar sem preencher campos
  102 |     await page.click('[data-testid="btn-salvar-evento"]');
  103 |     
  104 |     // Modal deve permanecer aberto (validação impediu salvamento)
  105 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  106 |     
  107 |     await page.click('[data-testid="btn-fechar-modal"]');
  108 |   });
  109 | 
  110 |   test('deve editar evento existente', async ({ page }) => {
  111 |     // Verificar se há eventos para editar
  112 |     const eventos = await page.locator('[data-testid="agenda-container"] .cursor-pointer').count();
  113 |     
  114 |     if (eventos === 0) {
  115 |       test.skip(true, 'Nenhum evento encontrado para editar');
  116 |       return;
  117 |     }
  118 |     
  119 |     // Clicar no primeiro evento
  120 |     await page.locator('[data-testid="agenda-container"] .cursor-pointer').first().click();
  121 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  122 | 
  123 |     // Modificar título
  124 |     await page.fill('[data-testid="input-titulo-evento"]', 'Evento editado E2E');
  125 |     await page.click('[data-testid="btn-salvar-evento"]');
  126 |     
  127 |     await expect(page.locator('[data-testid="modal-usuario"]')).not.toBeVisible();
  128 |   });
  129 | 
  130 |   test('deve selecionar tipo de evento', async ({ page }) => {
  131 |     await page.click('[data-testid="btn-novo-evento"]');
  132 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  133 | 
  134 |     await page.click('[data-testid="select-tipo-evento-modal"]');
> 135 |     await page.click('text=Reunião');
      |                ^ Error: page.click: Test timeout of 60000ms exceeded.
  136 |     
  137 |     const valorSelecionado = await page.locator('[data-testid="select-tipo-evento-modal"]').inputValue();
  138 |     expect(valorSelecionado).toBe('reuniao');
  139 |     
  140 |     await page.click('[data-testid="btn-cancelar-modal"]');
  141 |   });
  142 | 
  143 |   test('deve preencher endereço do evento', async ({ page }) => {
  144 |     await page.click('[data-testid="btn-novo-evento"]');
  145 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  146 | 
  147 |     await page.fill('[data-testid="input-endereco-modal"]', 'Rua Teste, 123 - São Paulo, SP');
  148 |     
  149 |     const endereco = await page.locator('[data-testid="input-endereco-modal"]').inputValue();
  150 |     expect(endereco).toBe('Rua Teste, 123 - São Paulo, SP');
  151 |     
  152 |     await page.click('[data-testid="btn-cancelar-modal"]');
  153 |   });
  154 | 
  155 |   test('deve preencher observações do evento', async ({ page }) => {
  156 |     await page.click('[data-testid="btn-novo-evento"]');
  157 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  158 | 
  159 |     await page.fill('[data-testid="textarea-observacoes-modal"]', 'Observações de teste E2E');
  160 |     
  161 |     const observacoes = await page.locator('[data-testid="textarea-observacoes-modal"]').inputValue();
  162 |     expect(observacoes).toBe('Observações de teste E2E');
  163 |     
  164 |     await page.click('[data-testid="btn-cancelar-modal"]');
  165 |   });
  166 | 
  167 |   test('deve selecionar cor do evento', async ({ page }) => {
  168 |     await page.click('[data-testid="btn-novo-evento"]');
  169 |     await expect(page.locator('[data-testid="modal-usuario"]')).toBeVisible();
  170 | 
  171 |     await page.fill('[data-testid="input-cor-modal"]', '#FF0000');
  172 |     
  173 |     const cor = await page.locator('[data-testid="input-cor-modal"]').inputValue();
  174 |     expect(cor).toBe('#FF0000');
  175 |     
  176 |     await page.click('[data-testid="btn-cancelar-modal"]');
  177 |   });
  178 | });
  179 | 
```