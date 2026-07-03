-- Rotate wide tables onto landscape pages. Only tables with at least
-- THRESHOLD columns are wrapped; everything else stays portrait.
-- Override via metadata: pandoc -M landscape-cols=6
local THRESHOLD = 6

function Meta(m)
  if m["landscape-cols"] then
    THRESHOLD = tonumber(pandoc.utils.stringify(m["landscape-cols"])) or THRESHOLD
  end
end

function Table(el)
  if #el.colspecs >= THRESHOLD then
    return {
      pandoc.RawBlock("latex", "\\begin{landscape}"),
      el,
      pandoc.RawBlock("latex", "\\end{landscape}"),
    }
  end
end
