<template>
  <v-btn-toggle
    v-model="active_tool_id"
    borderless
    class="transparent"
    >
    <span
      v-for="[id, {tooltip, icon, disabled, component_name}] of Object.entries(tools_data)"
      :key="id"
    >
      <component
        :id="component_name"
        v-if="component_name"
        :is="component_name"
      />
      {{ component_name }}
      <v-tooltip
        top
        v-if="!component_name"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            v-on="on"
            icon
            :value="id"
            :disabled="disabled"
          >
            <v-icon>{{ icon }}</v-icon>
          </v-btn>
        </template>
        <span>{{ tooltip }}</span>
      </v-tooltip>
    </span>
  </v-btn-toggle>
</template>

<script>
export default {
  mounted() {
    console.log(this);
  }
}
</script>
