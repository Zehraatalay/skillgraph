<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

import {
  analyzeSkills,
  extractDocument,
} from '@/services/skillAnalysisApi'

import JobMatchResults from '@/components/skill-analysis/JobMatchResults.vue'
import JobPostingList from '@/components/skill-analysis/JobPostingList.vue'


// Candidate information
const cvText = ref('')
const githubUsername = ref('')

// Job information
function createEmptyJob() {
  return {
    id: crypto.randomUUID(),
    title: '',
    company: '',
    description: '',
  }
}

const jobs = ref([createEmptyJob()])

// Analysis state
const loading = ref(false)
const errorMessage = ref('')
const analysisResult = ref(null)

// Document upload state
const selectedFile = ref(null)
const extractingDocument = ref(false)
const documentError = ref('')
const extractedFilename = ref('')

const MAX_FILE_SIZE = 5 * 1024 * 1024

async function handleFileChange(event) {
  const file = event.target.files?.[0]

  if (!file) return

  documentError.value = ''
  extractedFilename.value = ''
  selectedFile.value = null
  analysisResult.value = null
  cvText.value = ''

  const extension = file.name.split('.').pop()?.toLowerCase()

  if (!['pdf', 'docx'].includes(extension)) {
    documentError.value = 'Only PDF and DOCX files are supported.'
    event.target.value = ''
    return
  }

  if (file.size > MAX_FILE_SIZE) {
    documentError.value = 'File size must not exceed 5 MB.'
    event.target.value = ''
    return
  }

  extractingDocument.value = true

  try {
    const result = await extractDocument(file)

    cvText.value = result.text
    selectedFile.value = file
    extractedFilename.value = result.filename
  } catch (error) {
    documentError.value =
      error instanceof Error
        ? error.message
        : 'Document extraction failed.'

    event.target.value = ''
  } finally {
    extractingDocument.value = false
  }
}

function clearDocument() {
  selectedFile.value = null
  extractedFilename.value = ''
  documentError.value = ''
  cvText.value = ''
  analysisResult.value = null

  const input = document.getElementById('cv-file')

  if (input) {
    input.value = ''
  }
}

// Job management
function addJob() {
  jobs.value.push(createEmptyJob())
}

function removeJob(id) {
  if (jobs.value.length <= 1) {
    return
  }

  jobs.value = jobs.value.filter(
    (job) => job.id !== id
  )
}

function updateJob(updatedJob) {
  const index = jobs.value.findIndex(
    (job) => job.id === updatedJob.id
  )

  if (index === -1) {
    return
  }

  jobs.value[index] = updatedJob
}

// Real analysis
async function handleAnalyze() {
  if (loading.value || extractingDocument.value) {
    return
  }

  errorMessage.value = ''
  analysisResult.value = null

  const cv = cvText.value.trim()
  const github = githubUsername.value.trim()

  if (!cv && !github) {
    errorMessage.value =
      'Please upload a CV, enter CV text, or provide a GitHub username.'
    return
  }

  const normalizedJobs = jobs.value.map((job) => ({
    id: job.id,
    title: job.title.trim(),
    company: job.company.trim(),
    description: job.description.trim(),
  }))

  const hasIncompleteJob = normalizedJobs.some(
    (job) =>
      !job.title ||
      !job.company ||
      !job.description
  )

  if (hasIncompleteJob) {
    errorMessage.value =
      'Please complete the position, company, and description for every job.'
    return
  }

  loading.value = true

  try {
    const payload = {
      cv_text: cv || null,
      github_username: github || null,
      job_postings: normalizedJobs,
    }

    analysisResult.value = await analyzeSkills(payload)
  } catch (error) {
    errorMessage.value =
      error instanceof Error
        ? error.message
        : 'An unexpected error occurred.'
  } finally {
    loading.value = false
  }
}


</script>

<template>
  <div class="analysis-page">
    <!-- Header -->
    <header class="analysis-header">
      <RouterLink to="/" class="brand">
        <span class="brand-icon">SG</span>
        <span>SkillGraph</span>
      </RouterLink>

      <span class="header-label">
        Evidence-backed job matching
      </span>
    </header>

    <main class="analysis-container">
      <!-- Hero -->
      <section class="hero">
        <p class="eyebrow">
          AI-powered skill intelligence
        </p>

        <h1>
          Understand your skills.
          <span>Discover your opportunities.</span>
        </h1>

        <p>
          Analyze your CV and GitHub projects against job requirements
          using transparent, evidence-backed matching.
        </p>
      </section>

      <!-- Analysis Form -->
      <form
        class="analysis-form"
        @submit.prevent="handleAnalyze"
      >
        <div class="form-grid">
          <!-- Candidate Profile -->
          <section class="form-card">
            <h2>Candidate Profile</h2>

            <!-- CV Upload -->
            <div class="upload-section">
              <label for="cv-file">
                Upload CV (PDF or DOCX)
              </label>

              <input
                id="cv-file"
                type="file"
                accept=".pdf,.docx"
                :disabled="loading || extractingDocument"
                @change="handleFileChange"
              />

              <p class="upload-hint">
                Maximum file size: 5 MB
              </p>

              <p
                v-if="extractingDocument"
                class="upload-progress"
                role="status"
              >
                Extracting text from your CV...
              </p>

              <div
                v-if="extractedFilename"
                class="upload-success"
              >
                <span>
                  ✓ {{ extractedFilename }}
                </span>

                <span>
                  Text extracted successfully
                </span>

                <button
                  type="button"
                  class="remove-file-button"
                  :disabled="loading || extractingDocument"
                  @click="clearDocument"
                >
                  Remove
                </button>
              </div>

              <p
                v-if="documentError"
                class="error-message"
                role="alert"
              >
                {{ documentError }}
              </p>
            </div>

            <!-- Extracted / Manual CV Text -->
            <label for="cv">
              CV Text
            </label>

            <textarea
              id="cv"
              v-model="cvText"
              rows="11"
              placeholder="Upload your CV or paste its text here..."
              :disabled="loading || extractingDocument"
            />

            <p class="field-hint">
              You can review and edit the extracted text before analysis.
            </p>

            <!-- GitHub Username -->
            <label for="github">
              GitHub Username (Optional)
            </label>

            <input
              id="github"
              v-model="githubUsername"
              type="text"
              placeholder="e.g. octocat"
              autocomplete="off"
              :disabled="loading || extractingDocument"
            />
          </section>

          <!-- Job Postings -->
          <section class="form-card">
            <JobPostingList
              :jobs="jobs"
              :disabled="loading || extractingDocument"
              @add="addJob"
              @remove="removeJob"
              @update="updateJob"
            />
          </section>
        </div>

        <!-- Analysis Error -->
        <p
          v-if="errorMessage"
          class="error-message"
          role="alert"
        >
          {{ errorMessage }}
        </p>

        <!-- Submit -->
        <div class="submit-container">
          <button
            type="submit"
            :disabled="loading || extractingDocument"
          >
            {{
              extractingDocument
                ? 'Processing CV...'
                : loading
                  ? 'Analyzing...'
                  : 'Analyze My Skills'
            }}
          </button>

        </div>
      </form>

      <!-- Loading -->
      <section
        v-if="loading"
        class="loading-section"
        role="status"
      >
        <div class="loader"></div>

        <h2>Analyzing your profile</h2>

        <p>
          Extracting skill evidence and evaluating job requirements.
          This may take a little while.
        </p>
      </section>

      <!-- Results -->
      <JobMatchResults
        v-if="analysisResult"
        :analysis-result="analysisResult"
        :jobs="jobs"
      />
    </main>
  </div>
</template>

<style scoped>
.analysis-page {
  min-height: 100vh;
  background: #f7f9fc;
  color: #172033;
}

.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px max(24px, calc((100vw - 1180px) / 2));
  border-bottom: 1px solid #e2e8f0;
  background: white;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #172033;
  font-size: 1.1rem;
  font-weight: 800;
  text-decoration: none;
}

.brand-icon {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 11px;
  background: #172033;
  color: white;
  font-size: 0.75rem;
}

.header-label {
  color: #64748b;
  font-size: 0.85rem;
}

.analysis-container {
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
  padding-bottom: 100px;
}

.hero {
  max-width: 850px;
  margin: 0 auto;
  padding: 75px 0 55px;
  text-align: center;
}

.eyebrow {
  margin-bottom: 15px;
  color: #4f46e5;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2.5rem, 5vw, 4rem);
  line-height: 1.15;
  letter-spacing: -0.045em;
}

.hero h1 span {
  display: block;
  color: #4f46e5;
}

.hero > p:last-child {
  max-width: 650px;
  margin: 22px auto 0;
  color: #64748b;
  line-height: 1.7;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-card {
  padding: 30px;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: white;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

.form-card h2 {
  margin: 0 0 25px;
  font-size: 1.25rem;
}

.form-card label {
  display: block;
  margin: 20px 0 10px;
  color: #475569;
  font-size: 0.85rem;
  font-weight: 600;
}

.form-card textarea,
.form-card input {
  box-sizing: border-box;
  width: 100%;
  padding: 14px;
  border: 1px solid #cbd5e1;
  border-radius: 11px;
  outline: none;
  background: white;
  color: #172033;
  font: inherit;
  font-size: 0.9rem;
}

.form-card textarea {
  resize: vertical;
  line-height: 1.6;
}

.form-card textarea:focus,
.form-card input:focus {
  border-color: #4f46e5;
}

.field-hint {
  margin-top: 8px;
  color: #64748b;
  font-size: 0.8rem;
  line-height: 1.5;
}

/* CV Upload */

.upload-section {
  padding: 20px;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  background: #f8fafc;
}

.upload-section label {
  display: block;
  margin: 0 0 12px;
  font-weight: 700;
}

.upload-section input[type='file'] {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: white;
}

.upload-hint {
  margin: 10px 0 0;
  color: #64748b;
  font-size: 0.8rem;
}

.upload-progress {
  margin-top: 12px;
  color: #4f46e5;
  font-size: 0.85rem;
}

.upload-success {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 12px;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  background: #f0fdf4;
  color: #15803d;
  font-size: 0.85rem;
  font-weight: 600;
}

.remove-file-button {
  margin-left: auto;
  padding: 6px 10px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: white;
  color: #b91c1c;
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
}

/* Submit */

.submit-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 30px;
}

.submit-container button {
  padding: 15px 35px;
  border: none;
  border-radius: 12px;
  background: #4f46e5;
  color: white;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.submit-container button:hover {
  background: #4338ca;
}

.submit-container button:disabled,
.remove-file-button:disabled {
  cursor: wait;
  opacity: 0.6;
}

.submit-container .mock-button {
  border: 1px solid #c7d2fe;
  background: #eef2ff;
  color: #4338ca;
}

.submit-container .mock-button:hover {
  background: #e0e7ff;
}

/* Errors */

.error-message {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #fecaca;
  border-radius: 12px;
  background: #fef2f2;
  color: #b91c1c;
}

/* Loading */

.loading-section {
  padding: 55px 0;
  text-align: center;
}

.loader {
  width: 42px;
  height: 42px;
  margin: 0 auto 20px;
  border: 4px solid #e2e8f0;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 800ms linear infinite;
}

/* Results */

.results-section {
  margin-top: 50px;
  padding: 30px;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: white;
}

.results-section pre {
  max-height: 550px;
  overflow: auto;
  padding: 20px;
  border-radius: 12px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.8rem;
}

/* Responsive */

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 800px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .analysis-header {
    padding: 18px 20px;
  }

  .header-label {
    display: none;
  }

  .hero {
    padding-top: 50px;
  }
}
</style>