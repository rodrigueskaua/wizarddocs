<template>
  <div class="bg-dark-subtle-panel rounded-3 p-3 h-100 d-flex flex-column">
    <h2 class="fs-6 text-uppercase text-secondary mb-3">Documentos</h2>

    <label class="upload-dropzone mb-3" :class="{ uploading }">
      <input type="file" accept="application/pdf" class="d-none" @change="onFileChange" :disabled="uploading" />
      <span v-if="uploading">Enviando…</span>
      <span v-else>📄 Enviar PDF</span>
    </label>

    <p v-if="error" class="text-danger small">{{ error }}</p>

    <div class="flex-grow-1 overflow-auto">
      <p v-if="documents.length === 0" class="text-secondary small">Nenhum documento enviado ainda.</p>

      <button
        v-for="doc in documents"
        :key="doc.filename"
        type="button"
        class="document-item w-100 text-start"
        :class="{ active: doc.filename === selected }"
        @click="$emit('select', doc.filename === selected ? null : doc.filename)"
      >
        <div class="d-flex justify-content-between align-items-center gap-2">
          <span class="text-truncate">{{ doc.filename }}</span>
          <span class="text-secondary small remove-btn px-1" @click.stop="onRemove(doc.filename)">✕</span>
        </div>
        <div class="text-secondary small">{{ doc.pages }} página(s) · {{ doc.chunks }} trecho(s)</div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { deleteDocument, uploadPdf } from '@/services/api'

const props = defineProps({
  documents: { type: Array, required: true },
  selected: { type: String, default: null },
})
const emit = defineEmits(['select', 'refresh'])

const uploading = ref(false)
const error = ref('')

async function onFileChange(event) {
  const file = event.target.files[0]
  event.target.value = ''
  if (!file) return

  uploading.value = true
  error.value = ''
  try {
    await uploadPdf(file)
    emit('refresh')
  } catch (err) {
    error.value = err.message
  } finally {
    uploading.value = false
  }
}

async function onRemove(filename) {
  try {
    await deleteDocument(filename)
    if (props.selected === filename) emit('select', null)
    emit('refresh')
  } catch (err) {
    error.value = err.message
  }
}
</script>

<style scoped>
.bg-dark-subtle-panel {
  background: #1e2126;
}

.upload-dropzone {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  border: 1px dashed #495057;
  border-radius: 0.5rem;
  cursor: pointer;
  color: #adb5bd;
}

.upload-dropzone:hover {
  border-color: #7c5cff;
  color: #fff;
}

.upload-dropzone.uploading {
  opacity: 0.6;
  pointer-events: none;
}

.document-item {
  display: block;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.25rem;
  color: #e9ecef;
}

.document-item:hover {
  background: #262a31;
}

.document-item.active {
  border-color: #7c5cff;
  background: #262a31;
}

.remove-btn:hover {
  color: #ff6b6b;
}
</style>
