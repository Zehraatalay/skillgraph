<script setup>
defineProps({
  recommendation: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="recommendation-card">
    <div class="recommendation-header">
      <div>
        <p class="priority">{{ recommendation.priority }} priority</p>

        <h3>{{ recommendation.technology }}</h3>
      </div>

      <strong class="recommendation-score">
        {{ recommendation.score }}
      </strong>
    </div>

    <p class="reason">
      {{ recommendation.reason }}
    </p>

    <div class="based-on">
      <span>Şunlara dayanıyor:</span>

      <div>
        <span
          v-for="technology in recommendation.based_on"
          :key="technology"
          class="technology-tag"
        >
          {{ technology }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.recommendation-card {
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.recommendation-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.priority {
  margin: 0 0 6px;
  color: var(--primary);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.recommendation-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.recommendation-score {
  display: grid;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 14px;
  background: var(--primary-soft);
  color: var(--primary);
}

.reason {
  margin: 18px 0;
  color: var(--text-muted);
  font-size: 0.86rem;
  line-height: 1.6;
}

.based-on > span {
  color: var(--text-muted);
  font-size: 0.72rem;
}

.based-on > div {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 8px;
}

.technology-tag {
  padding: 5px 9px;
  border-radius: 7px;
  background: var(--background);
  color: var(--text);
  font-size: 0.73rem;
  font-weight: 600;
}
</style>
