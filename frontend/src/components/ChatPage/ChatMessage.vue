<template>
  <div class="d-flex" :class="message.role === 'user' ? 'justify-content-end' : 'justify-content-start'">
    <div class="message-bubble" :class="message.role">
      <p class="mb-0 message-text">{{ message.content }}</p>

      <div v-if="message.citations?.length" class="mt-2 pt-2 border-top border-secondary-subtle">
        <div class="small text-secondary mb-1">Fontes:</div>
        <div class="d-flex flex-wrap gap-1">
          <span v-for="citation in message.citations" :key="citation.index" class="citation-chip">
            [{{ citation.index }}] {{ citation.source }} · p.{{ citation.page }}
          </span>
        </div>
      </div>

      <div v-if="message.role === 'assistant' && message.provider" class="text-secondary small mt-1">
        {{ message.provider }}<span v-if="message.model"> · {{ message.model }}</span>
        <span v-if="message.grounded === false"> · sem apoio nos documentos</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: { type: Object, required: true },
})
</script>

<style scoped>
.message-bubble {
  max-width: 75%;
  padding: 0.6rem 0.9rem;
  border-radius: 0.9rem;
  margin-bottom: 0.75rem;
}

.message-text {
  white-space: pre-wrap;
}

.message-bubble.user {
  background: #7c5cff;
  color: #fff;
  border-bottom-right-radius: 0.2rem;
}

.message-bubble.assistant {
  background: #262a31;
  color: #e9ecef;
  border-bottom-left-radius: 0.2rem;
}

.citation-chip {
  background: #343a40;
  color: #adb5bd;
  border-radius: 999px;
  padding: 0.1rem 0.6rem;
  font-size: 0.75rem;
}
</style>
