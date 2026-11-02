import type { Register } from 'claude-code'

// Nástroje, jejichž výsledek se kreslí jako diff nebo obsah souboru.
const ZAPISY = new Set(['Edit', 'MultiEdit', 'Write', 'NotebookEdit'])

type Hunk = { lines?: unknown }

/** Spočítá přidané a odebrané řádky ze structuredPatch. */
const spocitej = (vystup: unknown): { pridano: number; odebrano: number; soubor: string } => {
  const v = (vystup ?? {}) as { structuredPatch?: unknown; filePath?: unknown; notebook_path?: unknown; content?: unknown; type?: unknown }
  let pridano = 0
  let odebrano = 0
  if (Array.isArray(v.structuredPatch)) {
    for (const hunk of v.structuredPatch as Hunk[]) {
      if (!Array.isArray(hunk?.lines)) continue
      for (const radek of hunk.lines as unknown[]) {
        if (typeof radek !== 'string') continue
        if (radek.startsWith('+')) pridano += 1
        else if (radek.startsWith('-')) odebrano += 1
      }
    }
  }
  // Nový soubor přes Write nemá patch, jen obsah.
  if (pridano === 0 && odebrano === 0 && v.type === 'create' && typeof v.content === 'string') {
    pridano = v.content.split('\n').length
  }
  const cesta = typeof v.filePath === 'string' ? v.filePath : typeof v.notebook_path === 'string' ? v.notebook_path : ''
  const soubor = cesta.split('/').pop() ?? cesta
  return { pridano, odebrano, soubor }
}

export const register: Register = on => {
  on('ui.render', { component: 'ToolResult' }, ($, e, next) => {
    // Chyby, rozbalený pohled (ctrl+o, --verbose) a ostatní nástroje kreslí Claude Code sám.
    if (!ZAPISY.has(e.props.tool) || e.props.isErrored || e.props.isExpanded) {
      return next(e)
    }
    const { pridano, odebrano, soubor } = spocitej(e.props.output)
    const { Box, Text } = $.ui.resolve(e)
    return (
      <Box>
        <Text dimColor>
          {'  ⎿  '}
          {soubor ? `${soubor} · ` : ''}
        </Text>
        <Text color="diffAdded">+{pridano}</Text>
        <Text dimColor> </Text>
        <Text color="diffRemoved">−{odebrano}</Text>
        <Text dimColor> (diff: ctrl+o)</Text>
      </Box>
    )
  })
}
