<template>
  <div class="chat-page d-flex vh-100">
    <aside class="chat-sidebar p-3">
      <DocumentPanel :documents="documents" :selected="selectedSource" @select="selectedSource = $event" @refresh="loadDocuments" />
    </aside>

    <main class="flex-grow-1 d-flex flex-column">
      <header class="chat-header px-4 py-3 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="fs-5 mb-0">🧙‍♂️ Wizard Docs</h1>
          <p class="small text-secondary mb-0">
            {{ selectedSource ? `Perguntando sobre: ${selectedSource}` : 'Perguntando sobre todos os documentos' }}
          </p>
        </div>
        <select v-model="provider" class="form-select form-select-sm bg-dark text-white border-secondary" style="width: auto">
          <option v-for="option in availableProviders" :key="option.name" :value="option.name">
            {{ option.name }}
          </option>
        </select>
      </header>

      <div ref="scrollArea" class="chat-messages flex-grow-1 overflow-auto px-4 py-3">
        <p v-if="messages.length === 0" class="text-secondary text-center mt-5">
          Envie um PDF na barra ao lado e faça uma pergunta sobre ele.
        </p>
        <ChatMessage v-for="(message, index) in messages" :key="index" :message="message" />
        <p v-if="asking" class="text-secondary small">Pensando…</p>
        <p v-if="error" class="text-danger small">{{ error }}</p>
      </div>

      <form class="chat-input px-4 py-3 d-flex gap-2" @submit.prevent="onAsk">
        <input
          v-model="question"
          type="text"
          class="form-control bg-dark text-white border-secondary"
          placeholder="Faça uma pergunta sobre os documentos enviados…"
          :disabled="asking"
        />
        <button type="submit" class="btn btn-purple" :disabled="asking || !question.trim() || documents.length === 0">
          Enviar
        </button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import DocumentPanel from '@/components/ChatPage/DocumentPanel.vue'
import ChatMessage from '@/components/ChatPage/ChatMessage.vue'
import { askQuestion, listDocuments, listProviders } from '@/services/api'

const documents = ref([])
const selectedSource = ref(null)
const messages = ref([])
const question = ref('')
const asking = ref(false)
const error = ref('')
const scrollArea = ref(null)

const provider = ref('local')
const availableProviders = ref([{ name: 'local' }])

async function loadDocuments() {
  try {
    const body = await listDocuments()
    documents.value = body.documents
  } catch (err) {
    error.value = err.message
  }
}

async function loadProviders() {
  try {
    const body = await listProviders()
    availableProviders.value = body.available
    provider.value = body.default
  } catch (err) {
    error.value = err.message
  }
}

async function onAsk() {
  const text = question.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  question.value = ''
  asking.value = true
  error.value = ''
  await scrollToBottom()

  try {
    const history = messages.value
      .slice(0, -1)
      .slice(-6)
      .map(({ role, content }) => ({ role, content }))

    const body = await askQuestion({
      question: text,
      provider: provider.value,
      source: selectedSource.value || undefined,
      history,
    })

    messages.value.push({
      role: 'assistant',
      content: body.answer,
      citations: body.citations,
      grounded: body.grounded,
      provider: body.provider,
      model: body.model,
    })
  } catch (err) {
    error.value = err.message
  } finally {
    asking.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  scrollArea.value?.scrollTo({ top: scrollArea.value.scrollHeight, behavior: 'smooth' })
}

onMounted(() => {
  loadDocuments()
  loadProviders()
})
</script>

<style scoped>
.chat-page {
  background: #16181c;
}

.chat-sidebar {
  width: 280px;
  min-width: 280px;
  border-right: 1px solid #262a31;
}

.chat-header,
.chat-input {
  border-bottom: 1px solid #262a31;
}

.chat-input {
  border-top: 1px solid #262a31;
  border-bottom: none;
}

.btn-purple {
  background: #7c5cff;
  color: #fff;
}

.btn-purple:hover {
  background: #6a4ce0;
  color: #fff;
}

.btn-purple:disabled {
  opacity: 0.5;
}
</style>
