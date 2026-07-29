<script setup>
import { computed, onMounted, ref } from 'vue'

import RepositoryCard from '@/components/RepositoryCard.vue'
import SkillCard from '@/components/SkillCard.vue'
import {
  analyzeDeveloper,
  checkBackendHealth,
  getDeveloperGraph,
  getDeveloperRecommendations,
  getDeveloperSkills,
  getGitHubPreview,
} from '@/services/api'

import RecommendationCard from '@/components/RecommendationCard.vue'

import DeveloperGraph from '@/components/DeveloperGraph.vue'

const username = ref('')
const loading = ref(false)
const errorMessage = ref('')
const backendOnline = ref(false)

const profile = ref(null)
const repositories = ref([])
const skillProfile = ref(null)

const hasResults = computed(() => {
  return profile.value !== null && skillProfile.value !== null
})

const topSkill = computed(() => {
  return skillProfile.value?.skills?.[0] ?? null
})

const recommendations = ref([])

const developerGraph = ref(null)

async function checkHealth() {
  try {
    await checkBackendHealth()
    backendOnline.value = true
  } catch {
    backendOnline.value = false
  }
}

async function handleAnalyze() {
  const normalizedUsername = username.value.trim()

  if (!normalizedUsername) {
    errorMessage.value = 'Lütfen bir GitHub kullanıcı adı gir.'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await analyzeDeveloper(normalizedUsername)

    const [previewResult, skillResult, recommendationResult, graphResult] = await Promise.all([
      getGitHubPreview(normalizedUsername),
      getDeveloperSkills(normalizedUsername),
      getDeveloperRecommendations(normalizedUsername),
      getDeveloperGraph(normalizedUsername),
    ])

    profile.value = previewResult.user
    repositories.value = previewResult.repositories
    skillProfile.value = skillResult
    recommendations.value = recommendationResult.recommendations
    developerGraph.value = graphResult
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : 'Analiz sırasında bilinmeyen bir hata oluştu.'
  } finally {
    loading.value = false
  }
}

function clearResults() {
  username.value = ''
  errorMessage.value = ''
  profile.value = null
  repositories.value = []
  skillProfile.value = null
  recommendations.value = []
  developerGraph.value = null
}

onMounted(checkHealth)
</script>

<template>
  <div class="home-page">
    <header class="navbar">
      <a class="brand" href="/">
        <span class="brand-icon">SG</span>
        <span>SkillGraph</span>
      </a>

      <div class="backend-status" :class="{ online: backendOnline }">
        <span class="status-dot"></span>
        {{ backendOnline ? 'API online' : 'API offline' }}
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="hero-content">
          <p class="eyebrow">GitHub Developer Intelligence</p>

          <h1>
            GitHub profilini
            <span>yetenek graph’ına</span>
            dönüştür.
          </h1>

          <p class="hero-description">
            Repository, programlama dili ve proje sinyallerini analiz ederek geliştiricinin
            teknoloji profilini Neo4j üzerinde oluşturur.
          </p>

          <form class="search-form" @submit.prevent="handleAnalyze">
            <div class="input-wrapper">
              <span>github.com/</span>

              <input
                v-model="username"
                type="text"
                autocomplete="off"
                placeholder="kullanici-adi"
                :disabled="loading"
              />
            </div>

            <button type="submit" :disabled="loading">
              {{ loading ? 'Analiz ediliyor...' : 'Profili analiz et' }}
            </button>
          </form>

          <p v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </p>
        </div>
      </section>

      <section v-if="loading" class="loading-section">
        <div class="loader"></div>
        <h2>GitHub profili analiz ediliyor</h2>
        <p>Repository’ler, diller ve Neo4j graph verileri hazırlanıyor.</p>
      </section>

      <template v-else-if="hasResults">
        <section class="results-header">
          <div class="profile-card">
            <img :src="profile.avatar_url" :alt="`${profile.login} profil fotoğrafı`" />

            <div class="profile-information">
              <p class="eyebrow">Developer profile</p>

              <h2>{{ profile.name || profile.login }}</h2>

              <a :href="profile.html_url" target="_blank" rel="noreferrer">
                @{{ profile.login }}
              </a>

              <p v-if="profile.bio" class="bio">
                {{ profile.bio }}
              </p>

              <div class="profile-metadata">
                <span v-if="profile.location">
                  {{ profile.location }}
                </span>

                <span v-if="profile.company">
                  {{ profile.company }}
                </span>
              </div>
            </div>

            <button class="secondary-button" @click="clearResults">Yeni analiz</button>
          </div>

          <div class="summary-grid">
            <article>
              <span>Repository</span>
              <strong>{{ skillProfile.skills.length ? repositories.length : 0 }}</strong>
            </article>

            <article>
              <span>Teknoloji</span>
              <strong>{{ skillProfile.technology_count }}</strong>
            </article>

            <article>
              <span>En güçlü alan</span>
              <strong>{{ topSkill?.technology || '—' }}</strong>
            </article>

            <article>
              <span>En yüksek skor</span>
              <strong>{{ topSkill?.score ?? '—' }}</strong>
            </article>
          </div>
        </section>

        <section v-if="developerGraph" class="content-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Neo4j visualization</p>
              <h2>Geliştirici bilgi graph’ı</h2>
            </div>

            <p>
              Node’ları sürükleyebilir, yakınlaştırabilir ve ayrıntıları görüntülemek için graph
              öğelerine tıklayabilirsin.
            </p>
          </div>

          <DeveloperGraph :graph="developerGraph" />
        </section>

        <section class="content-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Technology profile</p>
              <h2>Yetenek skorları</h2>
            </div>

            <p>
              Skorlar GitHub repository çeşitliliği, kod miktarı ve yıldız sinyallerine göre
              hesaplanır.
            </p>
          </div>

          <div class="skills-grid">
            <SkillCard
              v-for="skill in skillProfile.skills"
              :key="skill.technology"
              :skill="skill"
            />
          </div>
        </section>

        <section v-if="recommendations.length" class="content-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Recommendation engine</p>
              <h2>Sonraki öğrenme adımları</h2>
            </div>

            <p>
              Öneriler mevcut teknoloji skorları ve tamamlayıcı yetkinlik ilişkileri üzerinden
              hesaplanır.
            </p>
          </div>

          <div class="recommendations-grid">
            <RecommendationCard
              v-for="recommendation in recommendations"
              :key="recommendation.technology"
              :recommendation="recommendation"
            />
          </div>
        </section>

        <section class="content-section repositories-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Repository analysis</p>
              <h2>Analiz edilen projeler</h2>
            </div>

            <p>Fork olmayan {{ repositories.length }} public repository.</p>
          </div>

          <div class="repositories-grid">
            <RepositoryCard
              v-for="repository in repositories"
              :key="repository.id"
              :repository="repository"
            />
          </div>
        </section>
      </template>
    </main>

    <footer>SkillGraph · Vue · FastAPI · Neo4j</footer>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
}

.navbar {
  display: flex;
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
  padding: 22px 0;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  color: var(--text);
  font-weight: 800;
  text-decoration: none;
}

.brand-icon {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 11px;
  background: var(--text);
  color: white;
  font-size: 0.76rem;
}

.backend-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
}

.backend-status.online .status-dot {
  background: #22c55e;
}

.hero {
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
  padding: 90px 0 105px;
}

.hero-content {
  max-width: 850px;
  margin: 0 auto;
  text-align: center;
}

.eyebrow {
  margin: 0 0 12px;
  color: var(--primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
  color: var(--text);
  font-size: clamp(2.7rem, 7vw, 5.7rem);
  line-height: 1.03;
  letter-spacing: -0.055em;
}

.hero h1 span {
  color: var(--primary);
}

.hero-description {
  max-width: 680px;
  margin: 26px auto 35px;
  color: var(--text-muted);
  font-size: 1.04rem;
  line-height: 1.7;
}

.search-form {
  display: flex;
  max-width: 720px;
  margin: 0 auto;
  padding: 7px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
  box-shadow: var(--shadow-lg);
}

.input-wrapper {
  display: flex;
  flex: 1;
  align-items: center;
  padding-left: 15px;
}

.input-wrapper span {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.input-wrapper input {
  width: 100%;
  min-width: 0;
  padding: 14px 6px;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font: inherit;
}

.search-form button,
.secondary-button {
  border: 0;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.search-form button {
  padding: 0 24px;
  border-radius: 11px;
  background: var(--primary);
  color: white;
}

.search-form button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.error-message {
  max-width: 720px;
  margin: 18px auto 0;
  padding: 13px 16px;
  border: 1px solid #fecaca;
  border-radius: 11px;
  background: #fff1f2;
  color: #b91c1c;
  font-size: 0.88rem;
}

.loading-section {
  width: min(700px, calc(100% - 40px));
  margin: 30px auto 130px;
  padding: 55px;
  text-align: center;
}

.loader {
  width: 42px;
  height: 42px;
  margin: 0 auto 22px;
  border: 4px solid #e3e6ef;
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 800ms linear infinite;
}

.loading-section h2 {
  margin: 0;
}

.loading-section p {
  color: var(--text-muted);
}

.results-header,
.content-section {
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.profile-card img {
  width: 92px;
  height: 92px;
  border-radius: 22px;
  object-fit: cover;
}

.profile-information {
  flex: 1;
}

.profile-information h2 {
  margin: 0;
  font-size: 1.7rem;
}

.profile-information a {
  display: inline-block;
  margin-top: 5px;
  color: var(--primary);
  text-decoration: none;
}

.bio {
  max-width: 700px;
  margin: 12px 0 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.profile-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 12px;
  color: var(--text-muted);
  font-size: 0.84rem;
}

.secondary-button {
  padding: 11px 15px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: white;
  color: var(--text);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-top: 18px;
}

.summary-grid article {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
}

.summary-grid span {
  display: block;
  margin-bottom: 7px;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.summary-grid strong {
  font-size: 1.3rem;
}

.content-section {
  padding-top: 90px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 30px;
  margin-bottom: 24px;
}

.section-heading h2 {
  margin: 0;
  font-size: 2rem;
}

.section-heading > p {
  max-width: 480px;
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
  text-align: right;
}

.skills-grid,
.recommendations-grid,
.repositories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 17px;
}

.repositories-section {
  padding-bottom: 100px;
}

footer {
  padding: 30px 20px;
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.78rem;
  text-align: center;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 800px) {
  .hero {
    padding-top: 55px;
  }

  .search-form {
    flex-direction: column;
  }

  .search-form button {
    padding: 14px;
  }

  .profile-card {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .profile-information {
    min-width: calc(100% - 120px);
  }

  .summary-grid,
  .skills-grid,
  .recommendations-grid,
  .repositories-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    display: block;
  }

  .section-heading > p {
    margin-top: 10px;
    text-align: left;
  }
}

@media (max-width: 540px) {
  .navbar,
  .hero,
  .results-header,
  .content-section {
    width: min(100% - 24px, 1180px);
  }

  .hero h1 {
    font-size: 2.7rem;
  }

  .input-wrapper {
    padding-left: 9px;
  }

  .profile-card img {
    width: 70px;
    height: 70px;
  }

  .profile-information {
    min-width: calc(100% - 92px);
  }

  .secondary-button {
    width: 100%;
  }
}
</style>
