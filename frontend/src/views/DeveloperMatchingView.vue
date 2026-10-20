<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { matchDeveloper } from '@/services/api'

const username = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const seniority = ref('all')
const roleFamily = ref('all')
const matches = computed(() => result.value?.matches ?? [])
const seniorities = computed(() => [...new Set(matches.value.map(m => m.seniority).filter(Boolean))])
const roleFamilies = computed(() => [...new Set(matches.value.map(m => m.role_family).filter(Boolean))])
const filtered = computed(() => matches.value.filter(m =>
  (seniority.value === 'all' || m.seniority === seniority.value) &&
  (roleFamily.value === 'all' || m.role_family === roleFamily.value)
))
const label = value => String(value ?? '').replaceAll('_', ' ')
const skillList = value => Array.isArray(value) ? value : []

async function submit() {
  const name = username.value.trim()
  if (!name || loading.value) return
  loading.value = true
  error.value = ''
  result.value = null
  seniority.value = 'all'
  roleFamily.value = 'all'
  try {
    result.value = await matchDeveloper(name, 10)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Eşleştirme başarısız oldu.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page">
    <nav class="navigation" aria-label="Matching navigation">
      <RouterLink to="/">← Ana sayfa</RouterLink>
      <RouterLink to="/repository-matching">Repository Matching</RouterLink>
      <RouterLink to="/developer-matching" aria-current="page">Developer Matching</RouterLink>
    </nav>

    <section class="hero">
      <p class="eyebrow">SKILLGRAPH · DEVELOPER MATCHING</p>
      <h1>GitHub becerilerine uygun işleri keşfet.</h1>
      <p>Neo4j'de daha önce analiz edilmiş geliştirici profilini iş ilanlarındaki teknik gereksinimlerle karşılaştır.</p>
      <form @submit.prevent="submit" class="search-form">
        <label for="github-username" class="sr-only">GitHub kullanıcı adı</label>
        <input id="github-username" v-model="username" placeholder="GitHub kullanıcı adı (örn. Zehraatalay)" autocomplete="off" required />
        <button :disabled="loading" type="submit">{{ loading ? 'Eşleştiriliyor…' : 'İşleri eşleştir' }}</button>
      </form>
      <p v-if="error" class="error" role="alert">{{ error }}<br /><small>Profil henüz analiz edilmediyse önce ana sayfadan profil analizi yap.</small></p>
    </section>

    <template v-if="result">
      <section class="summary" aria-label="Analiz özeti">
        <div><span>Geliştirici</span><strong>{{ result.username }}</strong></div>
        <div><span>Tespit edilen beceri</span><strong>{{ result.detected_skill_count }}</strong></div>
        <div><span>Değerlendirilen ilan</span><strong>{{ result.total_jobs_evaluated }}</strong></div>
      </section>

      <section class="section">
        <h2>Tespit edilen beceriler</h2>
        <div class="chips"><span v-for="skill in skillList(result.detected_skills)" :key="skill" class="chip detected">{{ skill }}</span><span v-if="!result.detected_skills?.length">Beceri bulunamadı.</span></div>
      </section>

      <section class="section">
        <div class="heading"><div><p class="eyebrow">EŞLEŞME SONUÇLARI</p><h2>Önerilen roller</h2></div><span>{{ filtered.length }} sonuç</span></div>
        <div class="filters">
          <label>Seviye <select v-model="seniority"><option value="all">Tümü</option><option v-for="s in seniorities" :key="s" :value="s">{{ label(s) }}</option></select></label>
          <label>Rol ailesi <select v-model="roleFamily"><option value="all">Tümü</option><option v-for="f in roleFamilies" :key="f" :value="f">{{ label(f) }}</option></select></label>
        </div>
        <p v-if="!filtered.length" class="empty">Seçilen filtrelere uygun eşleşme yok.</p>
        <div class="cards">
          <article v-for="(match, index) in filtered" :key="match.job_id" class="card">
            <header class="card-header"><div><small>#{{ index + 1 }} · {{ label(match.role_family) }} · {{ label(match.seniority) }}</small><h3>{{ match.title }}</h3></div><strong class="score">{{ match.score }}/100</strong></header>
            <div class="progress" role="progressbar" :aria-valuenow="Math.min(100, Math.max(0, Number(match.score) || 0))" aria-valuemin="0" aria-valuemax="100" :aria-label="`${match.title} teknik uyum skoru`"><div :style="{ width: `${Math.min(100, Math.max(0, Number(match.score) || 0))}%` }"></div></div>
            <div class="skill-section"><h4>Eşleşen gerekli beceriler</h4><div class="chips"><span v-for="s in skillList(match.matched_required_skills)" :key="s" class="chip matched">{{ s }}</span><span v-if="!match.matched_required_skills?.length" class="muted">Yok</span></div></div>
            <div class="skill-section"><h4>Eksik gerekli beceriler</h4><div class="chips"><span v-for="s in skillList(match.missing_required_skills)" :key="s" class="chip missing">{{ s }}</span><span v-if="!match.missing_required_skills?.length" class="muted">Yok</span></div></div>
            <div v-if="match.matched_preferred_skills?.length" class="skill-section"><h4>Eşleşen tercih edilen beceriler</h4><div class="chips"><span v-for="s in match.matched_preferred_skills" :key="s" class="chip preferred">{{ s }}</span></div></div>
            <div v-if="match.missing_preferred_skills?.length" class="skill-section"><h4>Eksik tercih edilen beceriler</h4><div class="chips"><span v-for="s in match.missing_preferred_skills" :key="s" class="chip preferred">{{ s }}</span></div></div>
            <p v-if="match.technology_stack_id" class="stack">Teknoloji grubu: {{ label(match.technology_stack_id) }}</p>
          </article>
        </div>
      </section>
      <p class="disclaimer">Skorlar yalnızca GitHub'dan tespit edilen teknik becerilere dayanır; işe alınma olasılığı veya gerçek iş ilanı önerisi değildir.</p>
    </template>
  </main>
</template>

<style scoped>
.page{max-width:1150px;margin:0 auto;padding:32px 20px 80px}.navigation{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:24px}.navigation a{color:#414ac8;text-decoration:none;font-weight:700}.navigation a[aria-current]{color:#171923}.hero{padding:48px;border-radius:25px;background:#172033;color:white}.eyebrow{font-size:12px;letter-spacing:.13em;font-weight:800;color:#69dbb5}.hero h1{font-size:clamp(30px,5vw,56px);line-height:1.08;max-width:800px;margin:14px 0}.hero p{color:#c6ccda;line-height:1.6}.search-form{display:flex;gap:12px;margin-top:28px}.search-form input{flex:1;min-width:0;border-radius:12px;padding:16px;border:1px solid #647086;background:#253047;color:white}.search-form button{border:0;border-radius:12px;padding:16px 24px;background:#75e0bb;color:#12261e;font-weight:800;cursor:pointer}.search-form button:disabled{opacity:.6;cursor:wait}.error{color:#ffb2ac!important}.summary{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.summary>div,.card{border:1px solid #e0e5ed;background:white;border-radius:18px;padding:24px}.summary span{display:block;color:#697084;margin-bottom:8px}.summary strong{font-size:22px;overflow-wrap:anywhere}.section{margin-top:36px}.section h2{font-size:27px}.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{padding:7px 11px;border-radius:100px;font-size:13px;font-weight:700}.detected,.matched{background:#dff8ee;color:#176a50}.missing{background:#fff0e3;color:#a34f15}.preferred{background:#eef1ff;color:#4d5db7}.heading{display:flex;justify-content:space-between;align-items:center;gap:15px}.filters{display:flex;flex-wrap:wrap;gap:15px;margin:16px 0 22px}.filters label{font-weight:700;color:#596174}.filters select{margin-left:8px;padding:9px;border-radius:8px;border:1px solid #dce1ea;background:white}.cards{display:grid;gap:18px}.card-header{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}.card-header small,.muted,.stack{color:#737b8e}.card h3{font-size:22px;margin:8px 0}.score{white-space:nowrap;color:#176a50;font-size:25px}.progress{height:9px;border-radius:20px;background:#edf0f5;overflow:hidden;margin:18px 0}.progress>div{height:100%;background:#54cfa5}.skill-section{margin-top:18px}.skill-section h4{margin:0 0 9px;font-size:14px}.stack{margin-top:20px;font-size:13px}.disclaimer{font-size:13px;color:#697084;margin-top:28px}.empty{padding:22px;background:white;border-radius:12px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}@media(max-width:700px){.hero{padding:28px 20px}.search-form{flex-direction:column}.summary{grid-template-columns:1fr}.card-header{flex-direction:column}}
</style>
