<template>
  <v-container
    fluid
    class="px-8"
  >
    <v-radio-group
      v-model="column"
      column
      :disabled='complete'
    >
      <v-radio
        v-for="[index, option] of radioOptions.entries()"
        :key="index"
        :color="`${color(index)} lighten-1`"
        @change="selectChoice(index)"
      >
        <template v-slot:label>
          <div>
          {{ option }}
          </div>
        </template>
      </v-radio>
    </v-radio-group>
    <v-alert
      v-show="feedbackIndex !== null"
      outlined
      :color="`${color(feedbackIndex)}`"
      :type="complete ? 'success' : 'warning'"
    >
      <div
        v-html="feedbacks[feedbackIndex]"
      >
      </div>
      <div
        v-if="scoring && complete"
        class="text-right"
      >
        <strong>{{ `+ ${score} ${score == 1 ? 'point' : 'points'}` }}</strong>
        <v-icon
          class="ml-1"
          :color="`${color(feedbackIndex)}`"
        >
          mdi-piggy-bank
        </v-icon>
      </div>
    </v-alert>
  </v-container>
</template>

<script>
module.exports = {
  props: {
    feedbacks: Array,
    correctAnswers: {
      type: Array,
      default: []
    },
    scoring: {
      type: Boolean,
      default: true
    },
    neutralAnswers: {
      type: Array,
      default: []
    },
    points: {
      type: [Array, Function],
      default(_rawProps) {
        return function(ntries) { return Math.max(12 - 2 * ntries, 0); };
      }
    },
    radioOptions: Array,
    scoreTag: String,
    selectedCallback: Function,
    stage: {
      type: [Object, null],
      default: null
    },
    story: {
      type: [Object, null],
      default: null
    }
  },
  mounted() {
    if (!this.scoreTag) {
      return;
    }

    if (this.story !== null && this.stage !== null) {
      this.storyState = this.story;
      this.stageState = this.stage;
    } else {
      let comp = this.$parent;
      while (comp) {
        if (comp.$data.stage_state) {
          this.stageState = this.stage || comp.$data.stage_state;
        }
        if (comp.$data.story_state) {
          this.storyState = this.story || comp.$data.story_state;
          break;
        }
        comp = comp.$parent;
      }
    }

    if (this.storyState && this.scoreTag in this.storyState) {
      const data = this.storyState.mc_scoring[this.scoreTag];
      this.tries = data.tries - 1; // selectChoice adds a try
      this.selectChoice(data.choice);
    }
  },
  data: function () {
    return {
      column: null,
      colorRight: 'green',
      colorNeutral: 'orange',
      colorWrong: 'red',
      complete: false,
      feedbackIndex: null,
      tries: 0,
      score: 0,
      storyState: null
    };
  },
  methods: {
    selectChoice: function(index) {
      this.feedbackIndex = index;
      this.tries += 1;
      const correct = this.correctAnswers.includes(index);
      if (correct) {
        this.complete = true;
        this.score = this.scoring ? this.getScore(this.tries) : null;
        if (this.scoreTag !== undefined & this.storyState !== null) {
          document.dispatchEvent(
            new CustomEvent("mc-score", {
              detail: {
                tag: this.scoreTag,
                score: this.score,
                choice: this.feedbackIndex,
                tries: this.tries,
              }
            })
          );
        }
      }
      if (this.selectedCallback !== undefined) {
        this.selectedCallback({
          index: index,
          correct: correct,
          neutral: this.neutralAnswers.includes(index),
          tries: this.tries
        });
      }
    },
    color: function(index) {
      if (this.correctAnswers.includes(index)) {
        return this.colorRight;
      } else if (this.neutralAnswers.includes(index)) {
        return this.colorNeutral;
      } else {
        return this.colorWrong;
      }
    },
    getScore: function(ntries) {
      if (Array.isArray(this.points)) {
        return ntries <= this.points.length ? this.points[ntries-1] : 0;
      } else {
        return this.points(ntries);
      }
    }
  }
};
</script>
