<template>
  <div class="container">
    <div class="row justify-content-center py-5">
      <div class="col-md-8 text-center">
        <div class="error-container">
          <h1 class="display-1 text-muted">404</h1>
          <i class="bi bi-exclamation-triangle-fill display-1 text-warning mb-4"></i>
          <h2 class="mb-4">页面不存在</h2>
          <p class="lead mb-5">抱歉，您访问的页面不存在或已被移除。</p>
          <router-link to="/" class="btn btn-primary btn-lg">
            <i class="bi bi-house-door me-2"></i>返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.error-container {
  padding: 4rem 2rem;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}
</style> 