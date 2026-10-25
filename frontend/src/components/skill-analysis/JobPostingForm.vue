<script setup>
defineProps({
  job: {
    type: Object,
    required: true,
  },
  index: {
    type: Number,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  removable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:job', 'remove'])

function updateField(job, field, value) {
  emit('update:job', {
    ...job,
    [field]: value,
  })
}
</script>

<template>
  <div class="job-form">
    <div class="job-header">
      <h3>Job {{ index + 1 }}</h3>

      <button
        v-if="removable"
        type="button"
        class="remove-button"
        :disabled="disabled"
        @click="emit('remove')"
      >
        Remove
      </button>
    </div>

    <div class="field">
      <label :for="`job-title-${job.id}`">
        Position
      </label>

      <input
        :id="`job-title-${job.id}`"
        type="text"
        :value="job.title"
        placeholder="e.g. Junior Machine Learning Engineer"
        :disabled="disabled"
        @input="updateField(job, 'title', $event.target.value)"
      />
    </div>

    <div class="field">
      <label :for="`job-company-${job.id}`">
        Company
      </label>

      <input
        :id="`job-company-${job.id}`"
        type="text"
        :value="job.company"
        placeholder="e.g. Example Company"
        :disabled="disabled"
        @input="updateField(job, 'company', $event.target.value)"
      />
    </div>

    <div class="field">
      <label :for="`job-description-${job.id}`">
        Job Description
      </label>

      <textarea
        :id="`job-description-${job.id}`"
        :value="job.description"
        rows="8"
        placeholder="Paste the job description here..."
        :disabled="disabled"
        @input="updateField(job, 'description', $event.target.value)"
      />
    </div>
  </div>
</template>

<style scoped>
.job-form {
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: #f8fafc;
}

.job-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.job-header h3 {
  margin: 0;
  color: #172033;
  font-size: 1rem;
}

.remove-button {
  padding: 7px 12px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: white;
  color: #b91c1c;
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}

.field {
  margin-top: 16px;
}

.field label {
  display: block;
  margin-bottom: 8px;
  color: #475569;
  font-size: 0.85rem;
  font-weight: 600;
}

.field input,
.field textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: white;
  color: #172033;
  font: inherit;
  font-size: 0.9rem;
}

.field textarea {
  resize: vertical;
  line-height: 1.6;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #4f46e5;
}

.remove-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>