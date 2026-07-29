<script setup>
defineProps({
  repository: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="repository-card">
    <div class="repository-header">
      <div>
        <a :href="repository.html_url" target="_blank" rel="noreferrer">
          {{ repository.name }}
        </a>

        <p>
          {{ repository.description || 'Açıklama eklenmemiş.' }}
        </p>
      </div>

      <span v-if="repository.language" class="language">
        {{ repository.language }}
      </span>
    </div>

    <div class="repository-footer">
      <span>★ {{ repository.stargazers_count }}</span>
      <span>Fork {{ repository.forks_count }}</span>

      <span v-if="repository.archived" class="archived"> Archived </span>
    </div>

    <div v-if="repository.topics?.length" class="topics">
      <span v-for="topic in repository.topics" :key="topic">
        {{ topic }}
      </span>
    </div>
  </article>
</template>

<style scoped>
.repository-card {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
}

.repository-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.repository-header a {
  color: var(--text);
  font-weight: 700;
  text-decoration: none;
}

.repository-header a:hover {
  color: var(--primary);
}

.repository-header p {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.5;
}

.language {
  flex-shrink: 0;
  padding: 5px 9px;
  border-radius: 8px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
}

.repository-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.archived {
  color: #b45309;
}

.topics {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 14px;
}

.topics span {
  padding: 5px 8px;
  border-radius: 7px;
  background: var(--background);
  color: var(--text-muted);
  font-size: 0.72rem;
}
</style>
