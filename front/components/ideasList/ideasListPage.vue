<template>
  <Layout
    v-bind="{
      currentPage: 'IdeasList',
      pageOptions: mobileHeaderUiOptions
    }"
  >
    <v-layout class="ideas-list">
      <!-- Title Section -->
      <div class="titleDiv" hidden-sm-and-down>
        <v-layout class="titleText">{{ title }}</v-layout>
      </div>

      <!-- Idea List -->
      <ideas-list
        :ideas="ideas"
        :loading="loadingIdea"
        :allow-load-more="!!nextToken"
        @load-more="loadMoreIdeas"
      ></ideas-list>

      <!-- Add Idea Button -->
      <v-btn class="addBtn" fab to="/ideas/create">
        <v-icon>add</v-icon>
      </v-btn>

      <!-- Bottom snackbar message -->
      <visual-notifier ref="notifier"></visual-notifier>
    </v-layout>
  </Layout>
</template>

<script>
import Layout from '@/components/layout/Layout'
import IdeasList from '@/components/ideasList/ideasList'
import VisualNotifier from '@/components/VisualNotifier'
import loadIdeas from '@/components/ideasList/loadIdeas'

export default {
  name: 'IdeasListPage',
  components: { Layout, IdeasList, VisualNotifier },
  props: {
    initialIdeas: {
      type: Array,
      default: () => []
    },
    initialNextToken: {
      type: String,
      required: false
    },
    title: {
      type: String
    },
    endPoint: {
      type: String
    },
    endPointName: {
      type: String
    },
    endPointMode: {
      type: String,
      required: false
    },
    endPointVariables: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      ideas: [],
      nextToken: null,

      loadingIdea: false
    }
  },
  computed: {
    mobileHeaderUiOptions() {
      return {
        pageTitle: this.title
      }
    }
  },
  created() {
    this.ideas = this.initialIdeas
    this.nextToken = this.initialNextToken
  },
  methods: {
    getLoadIdeasParams() {
      return [this.$amplifyApi, this.endPointName, this.endPoint]
    },
    async loadMoreIdeas() {
      if (!this.nextToken) {
        return
      }
      this.loadingIdea = true
      const res = await loadIdeas(
        ...this.getLoadIdeasParams(),
        Object.assign({ nextToken: this.nextToken }, this.endPointVariables),
        this.endPointMode
      )
      this.nextToken = res.nextToken
      this.ideas = this.ideas.concat(res.ideas)
      this.loadingIdea = false
    }
  }
}
</script>

<style scoped lang="scss">
.ideas-list {
  padding-top: 50px;
  background: white;
  padding-bottom: 2vh;
  display: block;

  @media #{$small-screen} {
    padding-top: 0;
  }

  .titleDiv {
    text-align: center;
    // border: 1px solid red;
    min-height: 30px;

    .titleText {
      display: inline-block;
      margin-bottom: 20px;

      font-size: 17px;
      font-weight: 600;
      color: #232323;
    }
  }

  .addBtn {
    position: fixed;
    right: 40px;
    bottom: 30px;
  }
}
</style>