export function validarCPF(cpf: string): boolean {
  const cpfLimpo = cpf.replace(/\D/g, '')
  
  if (cpfLimpo.length !== 11) return false
  if (/^(\d)\1{10}$/.test(cpfLimpo)) return false
  
  let soma = 0
  for (let i = 0; i < 9; i++) {
    soma += parseInt(cpfLimpo[i]) * (10 - i)
  }
  let resto = (soma * 10) % 11
  if (resto === 10 || resto === 11) resto = 0
  if (resto !== parseInt(cpfLimpo[9])) return false
  
  soma = 0
  for (let i = 0; i < 10; i++) {
    soma += parseInt(cpfLimpo[i]) * (11 - i)
  }
  resto = (soma * 10) % 11
  if (resto === 10 || resto === 11) resto = 0
  if (resto !== parseInt(cpfLimpo[10])) return false
  
  return true
}

export function validarCNPJ(cnpj: string): boolean {
  const cnpjLimpo = cnpj.replace(/\D/g, '')
  
  if (cnpjLimpo.length !== 14) return false
  if (/^(\d)\1{13}$/.test(cnpjLimpo)) return false
  
  let tamanho = cnpjLimpo.length - 2
  let numeros = cnpjLimpo.substring(0, tamanho)
  const digitos = cnpjLimpo.substring(tamanho)
  let soma = 0
  let pos = tamanho - 7
  
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--
    if (pos < 2) pos = 9
  }
  
  let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11)
  if (resultado !== parseInt(digitos.charAt(0))) return false
  
  tamanho = tamanho + 1
  numeros = cnpjLimpo.substring(0, tamanho)
  soma = 0
  pos = tamanho - 7
  
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--
    if (pos < 2) pos = 9
  }
  
  resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11)
  if (resultado !== parseInt(digitos.charAt(1))) return false
  
  return true
}
