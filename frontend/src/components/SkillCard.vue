<script setup>
defineProps({
  skill: {
    type: Object,
    required: true,
  },
})

function formatNumber(value) {
  return new Intl.NumberFormat('tr-TR').format(value)
}
</script>

<template>
  <article class="skill-card">
    <div class="skill-header">
      <div>
        <h3>{{ skill.technology }}</h3>
        <p>{{ skill.level }}</p>
      </div>

      <strong class="score">{{ skill.score }}</strong>
    </div>

    <div
      class="progress-track"
      role="progressbar"
      :aria-valuenow="skill.score"
      aria-valuemin="0"
      aria-valuemax="100"
    >
      <div class="progress-value" :style="{ width: `${skill.score}%` }"></div>
    </div>

    <div class="skill-stats">
      <div>
        <span>Repository</span>
        <strong>{{ skill.repository_count }}</strong>
      </div>

      <div>
        <span>Kod miktarı</span>
        <strong>{{ formatNumber(skill.total_bytes) }}</strong>
      </div>

      <div>
        <span>Yıldız</span>
        <strong>{{ skill.total_stars }}</strong>
      </div>
    </div>

    <div v-if="skill.repositories?.length" class="repository-tags">
      <span v-for="repository in skill.repositories" :key="repository">
        {{ repository }}
      </span>
    </div>
  </article>
</template>

<style scoped>
.skill-card {
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.skill-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.skill-header h3 {
  margin: 0;
  font-size: 1.15rem;
}

.skill-header p {
  margin: 5px 0 0;
  color: var(--text-muted);
  font-size: 0.88rem;
}

.score {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: 1rem;
}

.progress-track {
  height: 8px;
  margin: 20px 0;
  overflow: hidden;
  border-radius: 99px;
  background: #e8ebf2;
}

.progress-value {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #5c6cff, #7c3aed);
  transition: width 500ms ease;
}

.skill-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.skill-stats div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.skill-stats span {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.skill-stats strong {
  font-size: 0.92rem;
}

.repository-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 18px;
}

.repository-tags span {
  padding: 5px 9px;
  border-radius: 7px;
  background: var(--background);
  color: var(--text-muted);
  font-size: 0.72rem;
}

@media (max-width: 540px) {
  .skill-stats {
    grid-template-columns: 1fr;
  }
}
</style>
