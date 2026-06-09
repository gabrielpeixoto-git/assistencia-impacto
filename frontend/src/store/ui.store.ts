import { create } from 'zustand'

interface UIState {
  sidebarAberta: boolean
  commandPaletteAberta: boolean
  toggleSidebar: () => void
  fecharSidebar: () => void
  abrirSidebar: () => void
  toggleCommandPalette: () => void
  abrirCommandPalette: () => void
  fecharCommandPalette: () => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarAberta: true,
  commandPaletteAberta: false,
  toggleSidebar: () => set((state) => ({ sidebarAberta: !state.sidebarAberta })),
  fecharSidebar: () => set({ sidebarAberta: false }),
  abrirSidebar: () => set({ sidebarAberta: true }),
  toggleCommandPalette: () => set((state) => ({ commandPaletteAberta: !state.commandPaletteAberta })),
  abrirCommandPalette: () => set({ commandPaletteAberta: true }),
  fecharCommandPalette: () => set({ commandPaletteAberta: false }),
}))
