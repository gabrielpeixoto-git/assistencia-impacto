import { useState, useRef, useEffect, Children, isValidElement } from 'react'
import { createPortal } from 'react-dom'
import type { SelectHTMLAttributes } from 'react'

type OptionData = { value: string; label: string; key: string }

function extractOptions(children: React.ReactNode): OptionData[] {
  const options: OptionData[] = []
  Children.forEach(children, child => {
    if (isValidElement(child) && child.type === 'option') {
      const p = child.props as any
      options.push({
        value: String(p.value ?? ''),
        label: String(p.children ?? ''),
        key: String(child.key ?? p.value ?? Math.random()),
      })
    }
  })
  return options
}

interface CustomSelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  onChange?: (e: { target: { value: string } }) => void
  'data-testid'?: string
}

const CustomSelect = ({ value, onChange, children, disabled, className = '', 'data-testid': dataTestId }: CustomSelectProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [dropdownPos, setDropdownPos] = useState({ top: 0, left: 0, width: 0 })
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const options = extractOptions(children)
  const selected = options.find(o => o.value === String(value))

  const handleOpen = () => {
    if (disabled) return
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect()
      setDropdownPos({
        top: rect.bottom + window.scrollY,
        left: rect.left + window.scrollX,
        width: rect.width,
      })
    }
    setIsOpen(true)
  }

  // Fechar ao clicar fora
  useEffect(() => {
    if (!isOpen) return
    const handleClickOutside = (e: MouseEvent) => {
      const clickedButton = buttonRef.current?.contains(e.target as Node)
      const clickedDropdown = dropdownRef.current?.contains(e.target as Node)
      if (!clickedButton && !clickedDropdown) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  return (
    <div style={{ position: 'relative', width: '100%' }} className={className}>
      <button
        ref={buttonRef}
        type="button"
        disabled={disabled}
        onClick={handleOpen}
        data-testid={dataTestId}
        style={{
          width: '100%', padding: '8px 16px', textAlign: 'left',
          backgroundColor: 'rgba(255,255,255,0.08)', color: '#F1F5F9',
          border: '1px solid rgba(255,255,255,0.2)', borderRadius: '8px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}
      >
        <span>{selected ? selected.label : (options[0]?.label ?? 'Selecione...')}</span>
        <span style={{ fontSize: '10px' }}>▼</span>
      </button>

      {isOpen && createPortal(
        <div
          ref={dropdownRef}
          data-testid="custom-select-dropdown"
          style={{
            position: 'absolute',
            top: dropdownPos.top,
            left: dropdownPos.left,
            width: dropdownPos.width,
            zIndex: 99999,
            backgroundColor: '#1A1D27',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
            maxHeight: '220px',
            overflowY: 'auto',
          }}
        >
          {options.map(opt => (
            <div
              key={opt.key}
              onClick={() => {
                onChange?.({ target: { value: opt.value } })
                setIsOpen(false)
              }}
              style={{
                padding: '10px 16px',
                color: String(value) === opt.value ? '#6C63FF' : '#F1F5F9',
                backgroundColor: String(value) === opt.value ? 'rgba(108, 99, 255, 0.1)' : 'transparent',
                cursor: 'pointer',
                fontSize: '14px',
              }}
              onMouseEnter={e => { e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)' }}
              onMouseLeave={e => {
                e.currentTarget.style.backgroundColor =
                  String(value) === opt.value ? 'rgba(108, 99, 255, 0.1)' : 'transparent'
              }}
            >
              {opt.label}
            </div>
          ))}
        </div>,
        document.body
      )}
    </div>
  )
}

CustomSelect.displayName = 'CustomSelect'
export default CustomSelect
