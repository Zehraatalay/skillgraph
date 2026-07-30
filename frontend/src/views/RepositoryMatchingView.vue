<script setup>
import { computed, ref } from "vue";

const repositoryUrl = ref(
  "https://github.com/zehraatalay/stylematch"
);

const loading = ref(false);
const error = ref("");
const result = ref(null);
const selectedSeniority = ref("all");

const availableSeniorities = computed(() => {
  if (!result.value) {
    return [];
  }

  return [
    ...new Set(
      result.value.matches.map(
        (match) => match.seniority
      )
    ),
  ];
});

const filteredMatches = computed(() => {
  if (!result.value) {
    return [];
  }

  if (selectedSeniority.value === "all") {
    return result.value.matches;
  }

  return result.value.matches.filter(
    (match) =>
      match.seniority ===
      selectedSeniority.value
  );
});

function scoreClass(score) {
  if (score >= 70) {
    return "score-high";
  }

  if (score >= 40) {
    return "score-medium";
  }

  return "score-low";
}
const API_URL =
  "http://127.0.0.1:8000/api/matching/repository";

async function analyzeRepository() {
  loading.value = true;
  error.value = "";
  result.value = null;
  selectedSeniority.value = "all";
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repository_url: repositoryUrl.value,
        limit: 10,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Repository analiz edilemedi."
      );
    }

    result.value = data;
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

function formatLabel(value) {
  return value.replaceAll("_", " ");
}
</script>

<template>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">SKILLGRAPH</p>

      <h1>
        GitHub projeni analiz et,
        uygun işleri keşfet.
      </h1>

      <p class="description">
        Repository teknolojilerini çıkarır ve
        200 yazılım ilanıyla karşılaştırır.
      </p>

      <form
        class="repository-form"
        @submit.prevent="analyzeRepository"
      >
        <input
          v-model="repositoryUrl"
          type="url"
          placeholder="https://github.com/user/repository"
          required
        />

        <button
          type="submit"
          :disabled="loading"
        >
          {{
            loading
              ? "Analiz ediliyor..."
              : "İşleri eşleştir"
          }}
        </button>
      </form>

      <p
        v-if="error"
        class="error"
      >
        {{ error }}
      </p>
    </section>

    <template v-if="result">
      <section class="summary">
        <div>
            <span>Repository</span>

            <a
                class="repository-link"
                :href="result.repository_url"
                target="_blank"
                rel="noopener noreferrer"
            >
                {{ result.repository }}
            </a>
        </div>

        <div>
          <span>Bulunan skill</span>
          <strong>
            {{ result.detected_skill_count }}
          </strong>
        </div>

        <div>
          <span>İncelenen ilan</span>
          <strong>
            {{ result.total_jobs_evaluated }}
          </strong>
        </div>
      </section>

      <section class="skills-section">
        <h2>Bulunan Skill’ler</h2>

        <div class="skill-list">
          <span
            v-for="skill in result.detected_skills"
            :key="skill"
            class="skill detected"
          >
            {{ skill }}
          </span>
        </div>
      </section>

      <section class="matches-section">
        <div class="section-heading">
            <div>
            <p class="eyebrow">
                EN İYİ SONUÇLAR
            </p>

            <h2>İş eşleşmeleri</h2>

            <p class="section-description">
                İlanlar teknik skill uyumuna göre
                yüksekten düşüğe sıralanmıştır.
            </p>
            </div>

            <span class="result-count">
            {{ filteredMatches.length }} sonuç
            </span>
        </div>

        <div class="filters">
            <button
            type="button"
            :class="{
                active: selectedSeniority === 'all',
            }"
            @click="selectedSeniority = 'all'"
            >
            Tümü
            </button>

            <button
            v-for="seniority in availableSeniorities"
            :key="seniority"
            type="button"
            :class="{
                active:
                selectedSeniority === seniority,
            }"
            @click="
                selectedSeniority = seniority
            "
            >
            {{ formatLabel(seniority) }}
            </button>
        </div>

        <div class="job-grid">
          <article
                v-for="(match, index) in filteredMatches"
                :key="match.job_id"
                class="job-card"
                >
                <div class="job-card-header">
                    <div>
                    <span class="ranking">
                        #{{ index + 1 }}
                    </span>

                    <h3>{{ match.title }}</h3>

                    <p>
                        {{ formatLabel(match.role_family) }}
                        ·
                        {{ formatLabel(match.seniority) }}
                    </p>
                    </div>

                    <div
                    class="score"
                    :class="scoreClass(match.score)"
                    >
                    <strong>
                        {{ match.score }}%
                    </strong>

                    <span>
                        {{
                        match.score >= 70
                            ? "Yüksek uyum"
                            : match.score >= 40
                            ? "Orta uyum"
                            : "Geliştirilebilir"
                        }}
                    </span>
                    </div>
                </div>

                <div class="progress">
                    <div
                    :style="{
                        width: `${match.score}%`,
                    }"
                    />
                </div>

                <div class="skill-group">
                    <h4>Eşleşen skill’ler</h4>

                    <div class="skill-list">
                    <span
                        v-for="skill in [
                        ...match.matched_required_skills,
                        ...match.matched_preferred_skills,
                        ]"
                        :key="skill"
                        class="skill matched"
                    >
                        {{ skill }}
                    </span>

                    <span
                        v-if="
                        match.matched_required_skills.length === 0 &&
                        match.matched_preferred_skills.length === 0
                        "
                        class="empty"
                    >
                        Eşleşen skill yok.
                    </span>
                    </div>
                </div>

                <div class="skill-group">
                    <h4>Geliştirilmesi gerekenler</h4>

                    <div class="skill-list">
                    <span
                        v-for="skill in match.missing_required_skills"
                        :key="skill"
                        class="skill missing"
                    >
                        {{ skill }}
                    </span>
                    </div>
                </div>
                <div
                    v-if="match.missing_preferred_skills.length"
                    class="skill-group optional-skills"
                >
                    <h4>Tercih edilen ek skill’ler</h4>

                    <div class="skill-list">
                        <span
                            v-for="skill in match.missing_preferred_skills"
                            :key="skill"
                            class="skill preferred"
                        >
                            {{ skill }}
                        </span>
                    </div>
                </div>
                <p class="stack">
                    Stack:
                    <strong>
                    {{ formatLabel(match.technology_stack_id) }}
                    </strong>
                </p>
                </article>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
.page {
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
  padding: 48px 0 80px;
}

.hero {
  padding: 52px;
  border-radius: 28px;
  background: #172033;
  color: white;
}

.eyebrow {
  margin: 0 0 12px;
  color: #75e0bb;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.16em;
}

.hero h1 {
  max-width: 760px;
  margin: 0;
  font-size: clamp(36px, 6vw, 64px);
  line-height: 1.05;
}

.description {
  max-width: 650px;
  margin: 22px 0 32px;
  color: #c6ccda;
  font-size: 18px;
  line-height: 1.6;
}

.repository-form {
  display: flex;
  gap: 12px;
}

.repository-form input {
  flex: 1;
  min-width: 0;
  padding: 17px 18px;
  border: 1px solid #414b60;
  border-radius: 13px;
  outline: none;
  background: #222c40;
  color: white;
}

.repository-form input:focus {
  border-color: #75e0bb;
}

.repository-form button {
  padding: 0 24px;
  border: none;
  border-radius: 13px;
  background: #75e0bb;
  color: #10231d;
  font-weight: 800;
  cursor: pointer;
}

.repository-form button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.error {
  margin: 18px 0 0;
  color: #ffaaa7;
}

.summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin: 24px 0;
}

.summary div {
  padding: 25px;
  border: 1px solid #e1e5ed;
  border-radius: 18px;
  background: white;
}

.summary span {
  display: block;
  margin-bottom: 7px;
  color: #737b8e;
}

.summary strong {
  font-size: 24px;
}

.skills-section,
.matches-section {
  margin-top: 38px;
}

.skills-section h2,
.matches-section h2 {
  margin: 0 0 18px;
  font-size: 29px;
}

.skill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill {
  padding: 7px 11px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.detected,
.matched {
  background: #dff8ee;
  color: #176a50;
}

.missing {
  background: #fff0e3;
  color: #a34f15;
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin-bottom: 18px;
}

.section-heading h2 {
  margin: 0;
}

.job-grid {
  display: grid;
  gap: 18px;
}

.job-card {
  padding: 25px;
  border: 1px solid #e1e5ed;
  border-radius: 20px;
  background: white;
}

.job-card-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.ranking {
  color: #777f91;
  font-size: 13px;
  font-weight: 800;
}

.job-card h3 {
  margin: 7px 0;
  font-size: 22px;
}

.job-card-header p {
  margin: 0;
  color: #6c7486;
  text-transform: capitalize;
}

.score {
  min-width: 85px;
  text-align: right;
}

.score strong {
  display: block;
  color: #176a50;
  font-size: 28px;
}

.score span {
  color: #737b8e;
  font-size: 12px;
}

.progress {
  height: 8px;
  margin: 22px 0;
  overflow: hidden;
  border-radius: 999px;
  background: #edf0f5;
}

.progress div {
  height: 100%;
  border-radius: inherit;
  background: #54cfa5;
}

.skill-group {
  margin-top: 18px;
}

.skill-group h4 {
  margin: 0 0 10px;
}

.preferred {
  background: #eef1ff;
  color: #4d5db7;
}

.optional-skills h4::after {
  content: " Opsiyonel";
  margin-left: 6px;
  color: #8a91a2;
  font-size: 12px;
  font-weight: 600;
}


.empty {
  color: #7c8495;
  font-size: 14px;
}

.stack {
  margin: 20px 0 0;
  color: #737b8e;
  font-size: 13px;
  text-transform: capitalize;
}

.section-description {
  margin: 8px 0 0;
  color: #737b8e;
  line-height: 1.5;
}

.result-count {
  padding: 8px 13px;
  border-radius: 999px;
  background: #eef1f6;
  color: #596174;
  font-size: 13px;
  font-weight: 700;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin-bottom: 20px;
}

.filters button {
  padding: 9px 15px;
  border: 1px solid #dce1ea;
  border-radius: 999px;
  background: white;
  color: #596174;
  font-weight: 700;
  text-transform: capitalize;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s,
    color 0.2s;
}

.filters button:hover {
  border-color: #75e0bb;
}

.filters button.active {
  border-color: #172033;
  background: #172033;
  color: white;
}

.score-high strong {
  color: #147a55;
}

.score-medium strong {
  color: #b46919;
}

.score-low strong {
  color: #667085;
}

.score-high span {
  color: #147a55;
}

.score-medium span {
  color: #b46919;
}

.score-low span {
  color: #667085;
}
.repository-link {
  color: #172033;
  font-size: 24px;
  font-weight: 800;
  text-decoration: none;
}

.repository-link:hover {
  color: #176a50;
  text-decoration: underline;
}
@media (max-width: 720px) {
  .page {
    width: calc(100% - 24px);
    padding-top: 24px;
  }

  .hero {
    padding: 32px 22px;
  }

  .repository-form {
    flex-direction: column;
  }

  .repository-form button {
    padding: 16px;
  }

  .summary {
    grid-template-columns: 1fr;
  }

  .job-card-header {
    flex-direction: column;
  }

  .score {
    text-align: left;
  }
}
</style>