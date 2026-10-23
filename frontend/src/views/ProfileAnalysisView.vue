<script setup>
import { ref } from 'vue'
const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
const username = ref('Zehraatalay'), repositories = ref([]), selected = ref([])
const loading = ref(false), analyzing = ref(false), error = ref(''), report = ref(null)
async function fetchJson(url, options) {
  const response = await fetch(url, options)
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : `HTTP ${response.status}`)
  return body
}
async function discover() {
  loading.value = true; error.value = ''; report.value = null; selected.value = []; repositories.value = []
  try {
    const data = await fetchJson(`${base}/profile-analysis/${encodeURIComponent(username.value.trim())}/repositories`)
    repositories.value = data.repositories || []
  } catch (e) { error.value = e.message } finally { loading.value = false }
}
async function analyze() {
  if (!selected.value.length || selected.value.length > 5) { error.value = 'Bir seferde 1–5 repository seç.'; return }
  analyzing.value = true; error.value = ''; report.value = null
  try {
    report.value = await fetchJson(`${base}/profile-analysis/analyze`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), repositories: selected.value })
    })
  } catch (e) { error.value = e.message } finally { analyzing.value = false }
}
</script>
<template>
  <main class="wrap">
    <nav><a href="/">← Ana sayfa</a> · <a href="/evidence-matching">Evidence matching</a></nav>
    <h1>GitHub Profil Analizi</h1>
    <p>Herkese açık repository'leri keşfet, seç ve kaynak koddan teknoloji kullanım kanıtlarını incele.</p>
    <form @submit.prevent="discover" class="row"><input v-model="username" placeholder="GitHub kullanıcı adı" required /><button :disabled="loading">{{ loading ? 'Yükleniyor…' : 'Repository’leri bul' }}</button></form>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <section v-if="repositories.length"><h2>Repository'ler ({{ repositories.length }})</h2>
      <p>Analiz için en fazla 5 repository seç. Diğerlerini sonraki istekte analiz edebilirsin.</p>
      <label v-for="repo in repositories" :key="repo.name" class="repo"><input type="checkbox" :value="repo.name" v-model="selected" /> <strong>{{ repo.name }}</strong> <span>{{ repo.language || '—' }}</span><small>{{ repo.description }}</small></label>
      <button @click="analyze" :disabled="analyzing || !selected.length || selected.length > 5">{{ analyzing ? 'Analiz ediliyor…' : `Seçilenleri analiz et (${selected.length})` }}</button>
    </section>
    <section v-if="report"><h2>Analiz sonuçları</h2><p>{{ report.note }}</p>
      <h3>Repository durumları</h3><ul><li v-for="r in report.repositories" :key="r.repository">{{ r.repository }} — {{ r.status }} <span v-if="r.error_type">({{ r.error_type }})</span></li></ul>
      <h3>Tespit edilen beceriler</h3><article v-for="skill in report.skills" :key="skill.name" class="skill"><strong>{{ skill.name }}</strong> — {{ skill.evidence_count }} kanıt<br/><small>{{ skill.repositories.join(', ') }}</small><details><summary>Kanıt örnekleri</summary><pre v-for="(e,i) in skill.evidence_samples" :key="i">{{ e.repository }} / {{ e.file }}
{{ e.quote }}</pre></details></article>
      <p>Bu ekran yalnızca AST teknoloji kullanımını analiz eder; Neo4j'e yazmaz ve iş eşleştirmesi yapmaz.</p>
    </section>
  </main>
</template>
<style scoped>
.wrap{max-width:960px;margin:45px auto;padding:24px;font-family:system-ui;color:#172033}.row{display:flex;gap:12px;margin:25px 0}.row input{flex:1;padding:12px;border:1px solid #b7c2d1;border-radius:8px}button{padding:12px 18px;background:#187d64;color:white;border:0;border-radius:8px;cursor:pointer}button:disabled{opacity:.5}.repo,.skill{display:block;padding:15px;margin:8px 0;background:#f5f8fb;border:1px solid #dde4ed;border-radius:10px}.repo small{display:block;margin:6px 0 0 25px;color:#64748b}.repo span{float:right;color:#64748b}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:12px}.error{color:#b91c1c}nav a{color:#187d64}
</style>
