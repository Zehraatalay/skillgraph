<script setup>
import { computed } from 'vue'

const props = defineProps({
  analysisResult: {
    type: Object,
    required: true,
  },
  jobs: {
    type: Array,
    required: true,
  },
})

const jobLookup = computed(() => {
  return new Map(
    props.jobs.map((job) => [job.id, job])
  )
})

const results = computed(() => {
  return (props.analysisResult.results ?? []).map((result) => ({
    ...result,
    job: jobLookup.value.get(result.job_id) ?? {},
  }))
})

function formatCoverage(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return 'N/A'
  }

  return `${Math.round(value * 100)}%`
}

function progressWidth(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return '0%'
  }

  const percentage = Math.max(
    0,
    Math.min(100, value * 100)
  )

  return `${percentage}%`
}

function supportLabel(level) {
  const labels = {
    full: 'Full match',
    partial: 'Partial match',
    none: 'Not matched',
  }

  return labels[level] ?? 'Unknown'
}

function evidenceStrengthLabel(level) {
  const labels = {
    tested: 'Tested',
    implementation_backed: 'Implementation-backed',
    self_reported: 'Self-reported',
    none: 'No evidence',
  }

  return labels[level] ?? 'Unknown'
}

function evidenceLabel(evidence) {
  const source = evidence.source ?? 'Unknown source'
  const type = evidence.evidence_type ?? ''

  return `${source} · ${type}`
}

function getEvidence(skillMatch) {
  const matchedEvidence = (
    skillMatch.matched_evidence ?? []
  )
    .map((item) => item.evidence)
    .filter(Boolean)

  const partialEvidence =
    skillMatch.partial_evidence ?? []

  return [...matchedEvidence, ...partialEvidence]
}

function getSkillSupport(explainedRequirement, skill) {
  return (
    explainedRequirement.skill_support ?? []
  ).find((item) => item.skill === skill)
}

function getSummary(result, priority) {
  return result.summary?.[priority] ?? null
}
</script>

<template>
  <div class="match-results">
    <div class="results-heading">
      <div>
        <p class="eyebrow">Analysis complete</p>
        <h2>Your Job Match Results</h2>
        <p>
          Explore how your skills and project evidence align
          with each position.
        </p>
      </div>

      <span class="result-count">
        {{ results.length }}
        {{ results.length === 1 ? 'position' : 'positions' }}
      </span>
    </div>

    <div
      v-if="results.length === 0"
      class="empty-state"
    >
      No matching results were returned.
    </div>

    <article
      v-for="result in results"
      :key="result.job_id"
      class="job-result-card"
    >
      <!-- Job header -->
      <div class="job-heading">
        <div>
          <p class="job-company">
            {{ result.job.company || 'Company' }}
          </p>

          <h3>
            {{ result.job.title || 'Job analysis' }}
          </h3>
        </div>

        <span
          class="semantic-badge"
          :class="result.match_result?.semantic_status"
        >
          Semantic:
          {{ result.match_result?.semantic_status ?? 'unknown' }}
        </span>
      </div>

      <!-- Coverage -->
      <div class="coverage-grid">
        <div class="coverage-card">
          <span>Required coverage</span>

          <strong>
            {{
              formatCoverage(
                result.match_result?.required_coverage
              )
            }}
          </strong>

          <div class="progress-track">
            <div
              class="progress-fill required"
              :style="{
                width: progressWidth(
                  result.match_result?.required_coverage
                ),
              }"
            />
          </div>
        </div>

        <div class="coverage-card">
          <span>Preferred coverage</span>

          <strong>
            {{
              formatCoverage(
                result.match_result?.preferred_coverage
              )
            }}
          </strong>

          <div class="progress-track">
            <div
              class="progress-fill preferred"
              :style="{
                width: progressWidth(
                  result.match_result?.preferred_coverage
                ),
              }"
            />
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="summary-grid">
        <div
          v-for="priority in ['required', 'preferred']"
          :key="priority"
          class="summary-card"
        >
          <h4>
            {{ priority === 'required' ? 'Required' : 'Preferred' }}
            requirements
          </h4>

          <template v-if="getSummary(result, priority)">
            <div class="summary-stats">
              <div>
                <strong>
                  {{ getSummary(result, priority).satisfied }}
                </strong>
                <span>Satisfied</span>
              </div>

              <div>
                <strong>
                  {{ getSummary(result, priority).partial }}
                </strong>
                <span>Partial</span>
              </div>

              <div>
                <strong>
                  {{ getSummary(result, priority).missing }}
                </strong>
                <span>Missing</span>
              </div>

              <div>
                <strong>
                  {{ getSummary(result, priority).total }}
                </strong>
                <span>Total</span>
              </div>
            </div>
          </template>

          <p v-else class="empty-text">
            No summary available.
          </p>
        </div>
      </div>

      <!-- Semantic warning -->
      <p
        v-if="result.match_result?.semantic_status === 'failed'"
        class="warning"
      >
        Semantic matching was unavailable. Results are based
        on deterministic matching only.
      </p>

      <!-- Requirements -->
      <div class="requirements-section">
        <h4>Requirement Breakdown</h4>

        <div
          v-if="!result.explained_requirements?.length"
          class="empty-state"
        >
          No detailed requirements available.
        </div>

        <div
          v-for="(explained, requirementIndex) in result.explained_requirements ?? []"
          :key="requirementIndex"
          class="requirement-group"
        >
          <div class="requirement-header">
            <div class="requirement-meta">
              <span class="priority-badge">
                {{ explained.requirement.priority }}
              </span>

              <span class="operator-badge">
                {{ explained.requirement.operator }}
              </span>
            </div>

            <span class="requirement-coverage">
              {{
                formatCoverage(
                  explained.requirement.coverage
                )
              }}
            </span>
          </div>

          <div
            v-for="(skillMatch, skillIndex) in explained.requirement.skills"
            :key="skillIndex"
            class="skill-row"
          >
            <div class="skill-row-header">
              <div>
                <strong class="skill-name">
                  {{ skillMatch.skill }}
                </strong>

                <p
                  v-if="getSkillSupport(explained, skillMatch.skill)"
                  class="evidence-strength"
                >
                  Evidence strength:
                  {{
                    evidenceStrengthLabel(
                      getSkillSupport(
                        explained,
                        skillMatch.skill
                      ).level
                    )
                  }}
                </p>
              </div>

              <span
                class="support-badge"
                :class="skillMatch.support_level"
              >
                {{ supportLabel(skillMatch.support_level) }}
              </span>
            </div>

            <div
              v-if="getEvidence(skillMatch).length"
              class="evidence-list"
            >
              <div
                v-for="(evidence, evidenceIndex) in getEvidence(skillMatch)"
                :key="evidenceIndex"
                class="evidence-item"
              >
                <span class="evidence-meta">
                  {{ evidenceLabel(evidence) }}
                </span>

                <p>
                  {{ evidence.description }}
                </p>

                <small v-if="evidence.reference">
                  {{ evidence.reference }}
                </small>
              </div>
            </div>

            <p v-else class="no-evidence">
              No supporting evidence identified.
            </p>
          </div>

          <p
            v-if="explained.requirement.evidence_text"
            class="requirement-explanation"
          >
            {{ explained.requirement.evidence_text }}
          </p>
        </div>
      </div>
    </article>
  </div>
</template>

<style scoped>
.match-results {
  margin-top: 48px;
}

.results-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #4f46e5;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.results-heading h2 {
  margin: 0;
  color: #172033;
  font-size: 1.8rem;
}

.results-heading p:last-child {
  color: #64748b;
  line-height: 1.6;
}

.result-count {
  padding: 9px 14px;
  border-radius: 20px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.job-result-card {
  margin-bottom: 24px;
  padding: 28px;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  background: white;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

.job-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.job-company {
  margin: 0 0 8px;
  color: #4f46e5;
  font-size: 0.85rem;
  font-weight: 700;
}

.job-heading h3 {
  margin: 0;
  color: #172033;
  font-size: 1.4rem;
}

.semantic-badge {
  padding: 7px 11px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.semantic-badge.completed {
  background: #dcfce7;
  color: #166534;
}

.semantic-badge.failed {
  background: #fef3c7;
  color: #92400e;
}

.coverage-grid,
.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 24px;
}

.coverage-card,
.summary-card {
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.coverage-card > span {
  display: block;
  margin-bottom: 12px;
  color: #64748b;
  font-size: 0.85rem;
}

.coverage-card strong {
  display: block;
  color: #172033;
  font-size: 2rem;
}

.progress-track {
  height: 8px;
  margin-top: 16px;
  overflow: hidden;
  border-radius: 10px;
  background: #e2e8f0;
}

.progress-fill {
  height: 100%;
  border-radius: 10px;
}

.progress-fill.required {
  background: #4f46e5;
}

.progress-fill.preferred {
  background: #0d9488;
}

.summary-card h4 {
  margin: 0 0 18px;
  color: #334155;
  font-size: 0.9rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  text-align: center;
}

.summary-stats div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-stats strong {
  color: #172033;
  font-size: 1.3rem;
}

.summary-stats span {
  color: #64748b;
  font-size: 0.72rem;
}

.warning {
  margin-top: 18px;
  padding: 12px;
  border-radius: 10px;
  background: #fffbeb;
  color: #92400e;
  font-size: 0.85rem;
}

.requirements-section {
  margin-top: 30px;
}

.requirements-section > h4 {
  margin-bottom: 18px;
  color: #172033;
  font-size: 1.05rem;
}

.requirement-group {
  margin-bottom: 18px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.requirement-header,
.skill-row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.requirement-header {
  margin-bottom: 16px;
}

.requirement-meta {
  display: flex;
  gap: 8px;
}

.priority-badge,
.operator-badge {
  padding: 5px 10px;
  border-radius: 8px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.operator-badge {
  background: #f1f5f9;
  color: #475569;
}

.requirement-coverage {
  color: #172033;
  font-size: 0.9rem;
  font-weight: 800;
}

.skill-row {
  margin-top: 12px;
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
}

.skill-name {
  color: #172033;
  font-size: 0.9rem;
}

.evidence-strength {
  margin: 7px 0 0;
  color: #64748b;
  font-size: 0.75rem;
}

.support-badge {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
}

.support-badge.full {
  background: #dcfce7;
  color: #166534;
}

.support-badge.partial {
  background: #fef3c7;
  color: #92400e;
}

.support-badge.none {
  background: #fee2e2;
  color: #991b1b;
}

.evidence-list {
  margin-top: 12px;
}

.evidence-item {
  margin-top: 10px;
  padding: 12px;
  border-radius: 9px;
  background: #f8fafc;
}

.evidence-meta {
  color: #4f46e5;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
}

.evidence-item p {
  margin: 8px 0;
  color: #334155;
  font-size: 0.85rem;
  line-height: 1.6;
}

.evidence-item small {
  color: #64748b;
  overflow-wrap: anywhere;
}

.no-evidence,
.empty-text {
  color: #94a3b8;
  font-size: 0.82rem;
}

.requirement-explanation {
  margin: 16px 0 0;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 0.85rem;
  line-height: 1.6;
}

.empty-state {
  padding: 20px;
  border-radius: 10px;
  background: #f8fafc;
  color: #64748b;
}

@media (max-width: 700px) {
  .results-heading,
  .job-heading {
    flex-direction: column;
  }

  .coverage-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .job-result-card {
    padding: 20px;
  }
}
</style>