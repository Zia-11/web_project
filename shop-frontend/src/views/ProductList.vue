<template>
    <div>
      <h1>Товары</h1>
  
      <div style="font-weight: bold; margin-bottom: 16px;">
        Всего товаров: {{ totalCount }}
      </div>
  
      <!-- Фильтрация и сортировка -->
      <form @submit.prevent="fetchProducts" style="margin-bottom: 20px">
        <input v-model="filters.search" placeholder="Поиск..." />
        <input v-model="filters.category" placeholder="Категория" />
        <input v-model="filters.price" placeholder="Цена" type="number" />
        <select v-model="filters.ordering">
          <option value="">Сортировка</option>
          <option value="price">Цена ↑</option>
          <option value="-price">Цена ↓</option>
          <option value="name">Название ↑</option>
          <option value="-name">Название ↓</option>
        </select>
        <button type="submit">Применить</button>
        <button type="button" @click="resetFilters">Сбросить</button>
      </form>
  
      <!-- Список товаров -->
      <!-- <ul>
        <li v-for="product in products" :key="product.id">
          {{ product.category }}: {{ product.name }} — {{ product.price }} руб.
          <button @click="deleteProduct(product.id)">Удалить</button>
        </li>
      </ul> -->
  
      <div
        v-for="(products, category) in groupedProducts"
        :key="category"
        style="margin-bottom: 20px"
      >
        <h2>{{ category }}</h2>
        <ul>
          <li v-for="product in products" :key="product.id">
            {{ product.name }} — {{ product.price }} руб.
            <button @click="deleteProduct(product.id)">Удалить</button>
          </li>
        </ul>
      </div>
  
      <!-- Форма добавления -->
      <form @submit.prevent="addProduct" style="margin-top: 20px">
        <input v-model="newProduct.name" placeholder="Название" required />
        <input
          v-model="newProduct.price"
          placeholder="Цена"
          type="number"
          required
        />
        <input v-model="newProduct.category" placeholder="Категория" />
        <input v-model="newProduct.description" placeholder="Описание" />
        <input
          v-model="newProduct.quantity"
          placeholder="Кол-во"
          type="number"
          min="1"
        />
        <button type="submit">Добавить</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  export default {
    data() {
      return {
        products: [],
        totalCount: 0, // новое поле для WebSocket
        filters: {
          search: "",
          category: "",
          price: "",
          ordering: "",
        },
        newProduct: {
          name: "",
          price: "",
          description: "",
          category: "",
          quantity: 1,
        },
        ws: null, // для хранения WebSocket соединения
      };
    },
    methods: {
      fetchProducts() {
        // Формируем query string из фильтров
        const params = {};
        if (this.filters.search) params.search = this.filters.search;
        if (this.filters.category) params.category = this.filters.category;
        if (this.filters.price) params.price = this.filters.price;
        if (this.filters.ordering) params.ordering = this.filters.ordering;
  
        axios
          .get("http://localhost:8000/api/products/", { params })
          .then((response) => {
            this.products = response.data.results;
          });
      },
      resetFilters() {
        this.filters = {
          search: "",
          category: "",
          price: "",
          ordering: "",
        };
        this.fetchProducts();
      },
      addProduct() {
        axios
          .post("http://localhost:8000/api/products/", this.newProduct)
          .then(() => {
            this.fetchProducts();
            this.newProduct = {
              name: "",
              price: "",
              description: "",
              category: "",
              quantity: 1,
            };
          });
      },
      deleteProduct(id) {
        axios
          .delete(`http://localhost:8000/api/products/${id}/`)
          .then(() => this.fetchProducts());
      },
      connectWebSocket() {
        const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
        this.ws = new WebSocket(`${ws_scheme}://localhost:8000/ws/products/count/`);
        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if ("count" in data) {
            this.totalCount = data.count;
          }
        };
        this.ws.onclose = () => {
          // Автоматический реконнект при разрыве соединения
          setTimeout(this.connectWebSocket, 2000);
        };
      },
    },
    mounted() {
      this.fetchProducts();
      this.connectWebSocket();
    },
    beforeUnmount() {
      if (this.ws) {
        this.ws.close();
      }
    },
    computed: {
      groupedProducts() {
        const groups = {};
        for (const product of this.products) {
          const category = product.category || "Без категории";
          if (!groups[category]) {
            groups[category] = [];
          }
          groups[category].push(product);
        }
        return groups;
      },
    },
  };
  </script>
  