<script setup>
import { onMounted, ref } from 'vue'

const apiStatus = ref('Backend kontrol ediliyor...')
const errorMessage = ref('')

async function checkBackend() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/health')

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`)
    }

    const data = await response.json()
    apiStatus.value = `${data.service}: ${data.status}`
  } catch (error) {
    apiStatus.value = 'Backend bağlantısı başarısız'
    errorMessage.value = error instanceof Error ? error.message : 'Bilinmeyen hata'
  }
}

onMounted(checkBackend)
</script>

<template>
  <main class="page">
    <section class="card">
      <p class="eyebrow">SkillGraph</p>
      <h1>Developer Skill Analysis</h1>
      <p class="description">
        GitHub profillerini analiz ederek geliştiricilerin teknoloji ve yetkinlik
        graph'ını oluşturur.
      </p>

      <div class="status">
        <strong>API durumu</strong>
        <span>{{ apiStatus }}</span>
      </div>

      <p v-if="errorMessage" class="error">
        {{ errorMessage }}
      </p>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #f5f7fb;
}

.card {
  width: min(600px, 100%);
  padding: 40px;
  border: 1px solid #e3e7ef;
  border-radius: 18px;
  background: white;
  box-shadow: 0 18px 50px rgba(30, 41, 59, 0.08);
}

.eyebrow {
  margin: 0 0 8px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 36px;
}

.description {
  margin: 16px 0 28px;
  line-height: 1.6;
}

.status {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 16px;
  border-radius: 10px;
  background: #f1f5f9;
}

.error {
  margin-top: 16px;
  color: #b91c1c;
}
</style>