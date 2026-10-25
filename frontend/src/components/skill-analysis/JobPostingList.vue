<script setup>
import JobPostingForm from './JobPostingForm.vue'

defineProps({
  jobs: {
    type: Array,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'add',
  'remove',
  'update',
])
</script>

<template>
  <div class="job-list">
    <div class="list-header">
      <h2>Target Jobs</h2>

      <span class="job-count">
        {{ jobs.length }} job{{ jobs.length === 1 ? '' : 's' }}
      </span>
    </div>

    <div class="job-items">
      <JobPostingForm
        v-for="(job, index) in jobs"
        :key="job.id"
        :job="job"
        :index="index"
        :disabled="disabled"
        :removable="jobs.length > 1"
        @update:job="emit('update', $event)"
        @remove="emit('remove', job.id)"
      />
    </div>

    <button
      type="button"
      class="add-button"
      :disabled="disabled"
      @click="emit('add')"
    >
      + Add Another Job
    </button>

    <p class="hint">
      Add multiple positions to compare your skills against
      different job requirements.
    </p>
  </div>
</template>

<style scoped>
.job-list {
  width: 100%;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.list-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.job-count {
  padding: 6px 12px;
  border-radius: 20px;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 0.8rem;
  font-weight: 700;
}

.job-items {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.add-button {
  width: 100%;
  margin-top: 18px;
  padding: 14px;
  border: 1px dashed #a5b4fc;
  border-radius: 12px;
  background: #eef2ff;
  color: #4338ca;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.add-button:hover {
  background: #e0e7ff;
}

.add-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.hint {
  margin-top: 12px;
  color: #64748b;
  font-size: 0.8rem;
  line-height: 1.5;
}
</style>