<template>
  <div class="bg-dark text-white p-4 rounded-3 shadow-lg w-100 max-w-md text-center">
    <div class="fs-1 mb-4">🧙‍♂️</div>
    <h1 class="fs-2 fw-bold mb-2">Bem-vindo(a) ao Wizard Docs</h1>
    <p class="fs-6 text-muted mb-4">
      👋 Olá! Bem-vindo(a) ao Wizard Docs, seu assistente inteligente de leitura e análise de documentos.
    </p>
    <p class="fs-6 text-secondary mb-6">
      Aqui, você pode carregar documentos e conversar com eles. É como ter um assistente que entende o conteúdo e responde às suas perguntas em linguagem natural.
      <br><br>
      Comece enviando um documento!
    </p>
    <button class="btn btn-purple hover:bg-purple-700 text-white py-2 px-5 rounded-3 transition" @click="$router.push('/chat')">
      Próximo
    </button>
    <DotsNavigation class="mt-4" />
  </div>
</template>

<script setup>
import DotsNavigation from './DotsNavigation.vue'
</script>