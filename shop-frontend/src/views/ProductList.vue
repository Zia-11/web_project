<template>
  <div>
    <h1>Товары</h1>

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
  },
  mounted() {
    this.fetchProducts();
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
