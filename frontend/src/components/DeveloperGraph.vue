<script setup>
import cytoscape from 'cytoscape'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  graph: {
    type: Object,
    required: true,
  },
})

const graphContainer = ref(null)
const selectedElement = ref(null)

let cy = null

function buildElements() {
  const nodes = props.graph.nodes.map((node) => ({
    data: {
      id: node.id,
      label: node.label,
      type: node.type,
      properties: node.properties,
    },
  }))

  const edges = props.graph.edges.map((edge) => ({
    data: {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type,
      properties: edge.properties,
    },
  }))

  return [...nodes, ...edges]
}

function createGraph() {
  if (!graphContainer.value) {
    return
  }

  cy?.destroy()

  cy = cytoscape({
    container: graphContainer.value,
    elements: buildElements(),

    layout: {
      name: 'cose',
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 45,
      nodeRepulsion: 700000,
      idealEdgeLength: 110,
      edgeElasticity: 120,
    },

    style: [
      {
        selector: 'node',
        style: {
          label: 'data(label)',
          width: 48,
          height: 48,
          'font-size': 10,
          'font-weight': 700,
          'text-wrap': 'wrap',
          'text-max-width': 90,
          'text-valign': 'bottom',
          'text-margin-y': 8,
          color: '#35394a',
          'background-color': '#a5adbd',
          'border-width': 2,
          'border-color': '#ffffff',
        },
      },
      {
        selector: 'node[type = "Developer"]',
        style: {
          width: 72,
          height: 72,
          'background-color': '#5b5ff5',
          color: '#171923',
        },
      },
      {
        selector: 'node[type = "Repository"]',
        style: {
          width: 55,
          height: 55,
          'background-color': '#f59e0b',
        },
      },
      {
        selector: 'node[type = "Technology"]',
        style: {
          'background-color': '#ec4899',
        },
      },
      {
        selector: 'node[type = "Topic"]',
        style: {
          width: 38,
          height: 38,
          'background-color': '#22c55e',
        },
      },
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': '#c7cbd6',
          'target-arrow-color': '#c7cbd6',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          label: 'data(type)',
          'font-size': 8,
          color: '#7c8293',
          'text-background-color': '#ffffff',
          'text-background-opacity': 1,
          'text-background-padding': 3,
        },
      },
      {
        selector: ':selected',
        style: {
          'border-width': 4,
          'border-color': '#171923',
          'line-color': '#5b5ff5',
          'target-arrow-color': '#5b5ff5',
        },
      },
    ],

    minZoom: 0.35,
    maxZoom: 2.5,
  })

  cy.on('tap', 'node', (event) => {
    const node = event.target

    selectedElement.value = {
      kind: 'node',
      label: node.data('label'),
      type: node.data('type'),
      properties: node.data('properties') || {},
    }
  })

  cy.on('tap', 'edge', (event) => {
    const edge = event.target

    selectedElement.value = {
      kind: 'edge',
      label: edge.data('type'),
      type: edge.data('type'),
      properties: edge.data('properties') || {},
    }
  })

  cy.on('tap', (event) => {
    if (event.target === cy) {
      selectedElement.value = null
    }
  })
}

function fitGraph() {
  cy?.fit(undefined, 45)
}

function resetLayout() {
  cy?.layout({
    name: 'cose',
    animate: true,
    fit: true,
    padding: 45,
  }).run()
}

watch(
  () => props.graph,
  async () => {
    await nextTick()
    createGraph()
  },
  {
    deep: true,
  },
)

onMounted(async () => {
  await nextTick()
  createGraph()
})

onBeforeUnmount(() => {
  cy?.destroy()
})
</script>

<template>
  <article class="graph-card">
    <header class="graph-toolbar">
      <div>
        <p class="eyebrow">Interactive graph</p>
        <h3>Developer knowledge graph</h3>
      </div>

      <div class="graph-actions">
        <button type="button" @click="fitGraph">Ekrana sığdır</button>

        <button type="button" @click="resetLayout">Yerleşimi yenile</button>
      </div>
    </header>

    <div class="graph-content">
      <div ref="graphContainer" class="graph-canvas"></div>

      <aside class="graph-sidebar">
        <div class="graph-summary">
          <div>
            <span>Node</span>
            <strong>{{ graph.node_count }}</strong>
          </div>

          <div>
            <span>İlişki</span>
            <strong>{{ graph.edge_count }}</strong>
          </div>
        </div>

        <div class="legend">
          <p>Graph açıklaması</p>

          <span>
            <i class="developer"></i>
            Developer
          </span>

          <span>
            <i class="repository"></i>
            Repository
          </span>

          <span>
            <i class="technology"></i>
            Technology
          </span>

          <span>
            <i class="topic"></i>
            Topic
          </span>
        </div>

        <div v-if="selectedElement" class="selection">
          <p>Seçili öğe</p>

          <h4>{{ selectedElement.label }}</h4>

          <span>{{ selectedElement.type }}</span>

          <dl v-if="Object.keys(selectedElement.properties).length">
            <template v-for="(value, key) in selectedElement.properties" :key="key">
              <dt>{{ key }}</dt>
              <dd>{{ value ?? '—' }}</dd>
            </template>
          </dl>
        </div>

        <div v-else class="selection empty">
          Bir node veya ilişkiye tıklayarak ayrıntıları görüntüle.
        </div>
      </aside>
    </div>
  </article>
</template>

<style scoped>
.graph-card {
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.graph-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 25px;
  padding: 22px 24px;
  border-bottom: 1px solid var(--border);
}

.graph-toolbar h3 {
  margin: 0;
  font-size: 1.2rem;
}

.graph-actions {
  display: flex;
  gap: 8px;
}

.graph-actions button {
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 9px;
  background: white;
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 0.78rem;
  font-weight: 700;
}

.graph-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  min-height: 570px;
}

.graph-canvas {
  min-width: 0;
  min-height: 570px;
  background: radial-gradient(circle, rgba(91, 95, 245, 0.08) 1px, transparent 1px);
  background-size: 22px 22px;
}

.graph-sidebar {
  padding: 20px;
  overflow: auto;
  border-left: 1px solid var(--border);
  background: #fafbfe;
}

.graph-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
}

.graph-summary div {
  padding: 13px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: white;
}

.graph-summary span {
  display: block;
  margin-bottom: 4px;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.graph-summary strong {
  font-size: 1.1rem;
}

.legend,
.selection {
  margin-top: 22px;
}

.legend > p,
.selection > p {
  margin: 0 0 12px;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.legend > span {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 9px;
  font-size: 0.8rem;
}

.legend i {
  width: 11px;
  height: 11px;
  border-radius: 50%;
}

.legend .developer {
  background: #5b5ff5;
}

.legend .repository {
  background: #f59e0b;
}

.legend .technology {
  background: #ec4899;
}

.legend .topic {
  background: #22c55e;
}

.selection {
  padding: 15px;
  border: 1px solid var(--border);
  border-radius: 13px;
  background: white;
}

.selection h4 {
  margin: 0;
  word-break: break-word;
}

.selection > span {
  display: block;
  margin-top: 5px;
  color: var(--primary);
  font-size: 0.75rem;
}

.selection dl {
  margin: 16px 0 0;
}

.selection dt {
  margin-top: 10px;
  color: var(--text-muted);
  font-size: 0.69rem;
}

.selection dd {
  margin: 3px 0 0;
  overflow-wrap: anywhere;
  font-size: 0.75rem;
}

.selection.empty {
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

@media (max-width: 850px) {
  .graph-content {
    grid-template-columns: 1fr;
  }

  .graph-sidebar {
    border-top: 1px solid var(--border);
    border-left: 0;
  }
}

@media (max-width: 600px) {
  .graph-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .graph-actions {
    width: 100%;
  }

  .graph-actions button {
    flex: 1;
  }

  .graph-canvas {
    min-height: 470px;
  }
}
</style>
