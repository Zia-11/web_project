<template>
  <div id="app">
    <ProductList />
  </div>
</template>

<script>
import ProductList from './views/ProductList.vue'

export default {
  name: 'App',
  components: {
    ProductList
  }
}
</script>
<style>
body {
  background: #0873a9;
  background: url('@/assets/bg.png') no-repeat center center fixed;
  background-size: cover;
}
</style>

