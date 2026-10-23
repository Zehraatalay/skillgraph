<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
const username = ref('Zehraatalay')
const limit = ref(10)
const loading = ref(false)
const error = ref('')
const response = ref(null)
const roleFamily = ref('all')
const families = computed(() => [...new Set((response.value?.matches || []).map(x => x.role_family))].sort())
const matches = computed(() => (response.value?.matches || []).filter(x => roleFamily.value === 'all' || x.role_family === roleFamily.value))
const pct = x => x == null ? 'N/A' : `${(x * 100).toFixed(1)}%`
const githubLink = e => {
  const repo = String(e.repository || '')
  const file = String(e.file || '')
  if (!/^[\w.-]+\/[\w.-]+$/.test(repo) || !file || file.startsWith('/') || file.split('/').includes('..')) return null
  return `https://github.com/${repo}/blob/HEAD/${file.split('/').map(encodeURIComponent).join('/')}`
}
async function submit() {
  if (loading.value || !username.value.trim()) return
  loading.value = true; error.value = ''; response.value = null
  try {
    const res = await fetch(`${API_BASE}/matching/developer/evidence`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({username: username.value.trim(), limit: Number(limit.value)})
    })
    const payload = await res.json().catch(() => null)
    if (!res.ok) throw new Error(typeof payload?.detail === 'string' ? payload.detail : `HTTP ${res.status}`)
    if (payload?.score_type !== 'verified_skill_coverage' || !Array.isArray(payload?.matches)) throw new Error('Unexpected evidence matching API response')
    response.value = payload
  } catch (e) { error.value = e.message || 'Connection failed' }
  finally { loading.value = false }
}
</script>

<template>
  <main class="page">
    <nav><RouterLink to="/">← Home</RouterLink> · <RouterLink to="/developer-matching">Developer matching</RouterLink></nav>
    <header><p class="eyebrow">SKILLGRAPH V10 · EVIDENCE EXPLORER</p><h1>Explainable job matching</h1><p>Explore verified code evidence behind each skill match. Scores represent weighted skill coverage, not hiring probability.</p></header>
    <form @submit.prevent="submit" class="form">
      <label>GitHub username <input v-model="username" maxlength="39" required autocomplete="off" /></label>
      <label>Results <select v-model.number="limit"><option :value="5">5</option><option :value="10">10</option><option :value="20">20</option></select></label>
      <button :disabled="loading">{{ loading ? 'Loading…' : 'Analyze evidence' }}</button>
    </form>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <template v-if="response">
      <section class="summary"><strong>{{ response.verified_skill_count }} evidence-backed skills</strong><span>{{ response.total_jobs_evaluated }} curated jobs evaluated</span><label>Role family <select v-model="roleFamily"><option value="all">All</option><option v-for="f in families" :key="f" :value="f">{{ f }}</option></select></label></section>
      <article v-for="match in matches" :key="match.job_id" class="card">
        <div class="row"><div><small>{{ match.role_family }} · {{ match.seniority }}</small><h2>{{ match.title }}</h2></div><strong class="score">{{ match.verified_skill_coverage_score }}/100</strong></div>
        <p>Required coverage: {{ pct(match.required_coverage) }} · Preferred coverage: {{ pct(match.preferred_coverage) }}</p>
        <section v-for="group in [{label:'Required', found:match.verified_required_skills, missing:match.unverified_required_skills},{label:'Preferred', found:match.verified_preferred_skills, missing:match.unverified_preferred_skills}]" :key="group.label">
          <h3>{{ group.label }} skills</h3>
          <p v-if="group.missing?.length"><b>Not evidenced:</b> {{ group.missing.join(', ') }}</p>
          <details v-for="skill in group.found || []" :key="skill.name" class="skill">
            <summary><b>{{ skill.name }}</b> · weight {{ skill.weight }} · {{ skill.evidence_count }} evidence records (up to 3 shown)</summary>
            <div v-for="(e, idx) in skill.evidence || []" :key="e.evidence_id || idx" class="evidence">
              <p><b>{{ e.repository }}</b> · {{ e.file }} <a v-if="githubLink(e)" :href="githubLink(e)" target="_blank" rel="noopener noreferrer">View on GitHub ↗</a></p>
              <pre>{{ e.quote }}</pre><p v-if="e.explanation">{{ e.explanation }}</p>
            </div>
          </details>
        </section>
      </article>
      <p class="disclaimer">Not evidenced ≠ no skill. GitHub links point to the current HEAD and may differ from the analyzed snapshot. Evidence quantity is not proficiency.</p>
    </template>
  </main>
</template>

<style scoped>
.page{max-width:1050px;margin:auto;padding:32px 20px 90px;font-family:system-ui,sans-serif;color:#17223b}a{color:#304bc2}header{background:#17243c;color:white;padding:35px;border-radius:20px;margin:22px 0}header p{max-width:700px;line-height:1.6;color:#d1daeb}.eyebrow{font-size:12px;letter-spacing:2px;color:#8ee6c5}.form,.summary,.row{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}.form,.summary{padding:20px;background:#f1f5fb;border-radius:14px;margin-bottom:22px}.form label{display:grid;gap:6px}.form input,.form select,.summary select{padding:10px;border:1px solid #c6d0de;border-radius:8px}button{background:#166b57;color:white;border:0;border-radius:8px;padding:13px 20px;cursor:pointer}button:disabled{opacity:.5}.card{border:1px solid #d8e1ed;border-radius:16px;padding:24px;margin:18px 0;background:white}.card h2{margin:5px 0}.score{font-size:24px;color:#14765d}.skill{padding:12px;margin:9px 0;background:#f4f7fc;border-radius:10px}.skill summary{cursor:pointer}.evidence{padding:10px;border-top:1px solid #dbe4ef;margin-top:10px;overflow-wrap:anywhere}.evidence pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#e8edf6;padding:12px;border-radius:7px}.error{color:#b42318}.disclaimer{font-size:13px;color:#66758a}
</style>
