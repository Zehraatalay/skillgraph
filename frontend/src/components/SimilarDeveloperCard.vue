<script setup>
defineProps({
  developer: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article class="developer-card">
    <div class="developer-main">
      <img
        v-if="developer.avatar_url"
        :src="developer.avatar_url"
        :alt="`${developer.login} profil fotoğrafı`"
      />

      <div class="avatar-placeholder" v-else>
        {{ developer.login.slice(0, 2).toUpperCase() }}
      </div>

      <div class="identity">
        <h3>
          {{ developer.name || developer.login }}
        </h3>

        <a v-if="developer.html_url" :href="developer.html_url" target="_blank" rel="noreferrer">
          @{{ developer.login }}
        </a>

        <span v-else> @{{ developer.login }} </span>
      </div>

      <strong class="similarity-score"> %{{ developer.similarity_score }} </strong>
    </div>

    <div class="similarity-progress">
      <div
        :style="{
          width: `${developer.similarity_score}%`,
        }"
      ></div>
    </div>

    <div class="shared-section">
      <p>
        {{ developer.shared_technology_count }}
        ortak teknoloji
      </p>

      <div class="technology-list">
        <span v-for="technology in developer.shared_technologies" :key="technology">
          {{ technology }}
        </span>
      </div>
    </div>

    <details>
      <summary>Tüm teknolojileri göster</summary>

      <div class="technology-list all">
        <span v-for="technology in developer.candidate_technologies" :key="technology">
          {{ technology }}
        </span>
      </div>
    </details>
  </article>
</template>

<style scoped>
.developer-card {
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.developer-main {
  display: flex;
  align-items: center;
  gap: 14px;
}

.developer-main img,
.avatar-placeholder {
  width: 54px;
  height: 54px;
  flex-shrink: 0;
  border-radius: 15px;
}

.developer-main img {
  object-fit: cover;
}

.avatar-placeholder {
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 800;
}

.identity {
  min-width: 0;
  flex: 1;
}

.identity h3 {
  margin: 0;
  overflow: hidden;
  font-size: 1rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.identity a,
.identity span {
  display: block;
  margin-top: 4px;
  color: var(--primary);
  font-size: 0.8rem;
  text-decoration: none;
}

.similarity-score {
  color: var(--primary);
  font-size: 1.05rem;
}

.similarity-progress {
  height: 7px;
  margin: 18px 0;
  overflow: hidden;
  border-radius: 999px;
  background: #e8ebf2;
}

.similarity-progress div {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #5b5ff5, #7c3aed);
}

.shared-section p {
  margin: 0 0 9px;
  color: var(--text-muted);
  font-size: 0.76rem;
}

.technology-list {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.technology-list span {
  padding: 5px 9px;
  border-radius: 7px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: 0.72rem;
  font-weight: 700;
}

details {
  margin-top: 17px;
}

summary {
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.76rem;
}

.technology-list.all {
  margin-top: 12px;
}

.technology-list.all span {
  background: var(--background);
  color: var(--text-muted);
}
</style>
