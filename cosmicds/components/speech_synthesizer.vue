<template>
  <span>
    <slot>
      <v-btn
        icon
      >
        <v-icon
          @click="(_event) => speak()"
        >
          {{ speaking ? 'mdi-stop' : 'mdi-voice' }}
        </v-icon>
      </v-btn>
    </slot>
  </span>
</template>

<script>
module.exports = {
  props: {
    selectors: {
      type: Array,
      default: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', ':not(mjx-assistive-mml) > mjx-container']
    },
    stopOnClose: {
      type: Boolean,
      default: true
    },
    root: {
      type: [Object, Function],
      default: null
    },
    autospeakOnChange: {
      type: [Boolean, Number],
      default: null
    },
    speakFlag: {
      type: Boolean,
      default: false
    }
  },
  data: function () {
    return {
      hasAutospoken: false,
      utteranceSpeaking: false,
      speakingTimeoutID: null,
      intervalID: 0,
      rootElement: null,
      iconNameMap: {
        'cached': 'reset'
      },
      speechSettings: {
        autoread: false,
        pitch: 1,
        rate: 1
      },
      responseHandler: null,
      updateHandler: null
    };
  },
  mounted() {
    this.responseHandler = (e) => {
      console.log("Got response");
      console.log(e.detail);
      this.speechSettings = e.detail;
      console.log(this.speechSettings);
      if (!this.hasAutospoken) {
        this.triggerAutospeak();
      }
      document.removeEventListener('speech-settings-response', this.responseHandler);
      this.responseHandler = null;
    };
    document.addEventListener('speech-settings-response', this.responseHandler);
    
    this.updateHandler = (e) => {
      console.log("Got update");
      this.speechSettings = e.detail;
    };
    document.addEventListener('speech-settings-update', this.updateHandler);
    console.log("About to dispatch event");
    document.dispatchEvent(new CustomEvent('speech-settings-request'));
    console.log(this);
    console.log(this.$root.$children[0].$children[0]);
    if (!(this.speaking && window.speechSynthesis.speaking)) {
      this.triggerAutospeak();
    }
  },
  destroyed() {
    console.log("Destroying!");
    if (this.responseHandler) {
      document.removeEventListener('speech-settings-response', this.responseHandler);
    }
    document.removeEventListener('speech-settings-update', this.updateHandler);

    if (this.stopOnClose && this.speaking) {
      clearInterval(this.intervalID);
      window.speechSynthesis.cancel();
    }
  },
  computed: {
    speaking: {
      get() {
        return this.utteranceSpeaking;
      },
      set(value) {
        if (this.speakingTimeoutID) {
          clearTimeout(this.speakingTimeoutID);
        }
        this.speakingTimeoutID = setTimeout(() => {
          this.utteranceSpeaking = value;
        }, 400);
      }
    }
  },
  methods: {

    triggerAutospeak() {
      if (this.speechSettings.autoread) {
        this.$nextTick(() => {
          this.hasAutospoken = true;
          this.speak(true);
        });
      }
    },

    elementText(element) {

      // Replace any MDI icons with text representing their name
      const clone = element.cloneNode(true);
      const mdiPrefix = "mdi-";
      const icons = clone.querySelectorAll(`[class*='${mdiPrefix}']`);
      icons.forEach(icon => {
        const classes = [...icon.classList].filter(cls => cls.startsWith(mdiPrefix));
        if (classes.length === 0) {
          icon.remove();
        } else {
          const txt = document.createElement("text");
          const cls = classes[0];
          let iconName = cls.slice(mdiPrefix.length);
          txt.textContent = this.iconNameMap[iconName] ?? iconName.replace("-", " ");
          icon.parentNode?.replaceChild(txt, icon);
        }
      });

      // Replace any MathJax with its semantic speech text
      if (clone.tagName === "mjx-container") {
        const speechText = clone.getAttribute("aria-label");
        if (speechText) {
          const txt = document.createElement("text");
          txt.textContent = speechText;
          clone.parentNode?.replaceChild(txt, clone);
        } else {
          clone.remove();
        }
      }

      return clone.textContent.trim();

    },
    makeUtterance(text) {
      const utterance = new SpeechSynthesisUtterance(text);

      Object.keys(this.speechSettings).forEach(key => {
        utterance[key] = this.speechSettings[key];
      });

      // The interval is to work around this issue:
      // https://bugs.chromium.org/p/chromium/issues/detail?id=679437
      //
      // We could just use one interval for the entire block of text items
      // but the pause-resume is sometimes slightly audible, so better to minimize that.
      // Note that the pause-resume won't happen if the text takes longer than 14 seconds to say
      utterance.onstart = (_event) => {
        console.log("Utterance onstart");
        this.intervalID = setInterval(() => {
          console.log("Here");
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        }, 14000);
        this.speaking = true;
      }
      utterance.onend = (_event) => {
        console.log("Utterance onend");
        this.speaking = false;
        clearInterval(this.intervalID);
      }

      return utterance;
    },
    findRootElement() {
      if (this.root instanceof Element) {
        this.rootElement = this.root;
      } else if (this.root instanceof Function) {
        this.rootElement = this.root();
      } else {
        this.rootElement = this.$parent.$el;
      }
    },
    // Taken from https://www.geeksforgeeks.org/how-to-check-if-an-element-is-visible-in-dom/
    // TODO: Is there a better way to check?
    //
    // Note that element.checkVisibility() doesn't work on Safari:
    // https://caniuse.com/mdn-api_element_checkvisibility
    isElementVisible(element) {
      if (element.checkVisibility) {
        return element.checkVisibility();
      }
      return element.offsetWidth || 
             element.offsetHeight || 
             element.getClientRects().length;
    },
    getSpeechItems() {
      if (this.rootElement === null) {
        this.findRootElement();
      }
      console.log(this.rootElement);
      const selectedElements = this.rootElement.querySelectorAll(this.selectors.join(","));
      console.log(this.selectors);
      const elements = [].concat(...selectedElements).filter(this.isElementVisible);
      elements.forEach(el => {
        console.log(el);
        console.log(this.isElementVisible(el));
        console.log(this.elementText(el));
      });
      const items = elements.map(element => this.elementText(element)).filter(text => text.length > 0);
      console.log(items);
      return items;
    },

    speak(forceSpeak=false) {
      const synth = window.speechSynthesis;
      if (synth.speaking) {
        synth.cancel();
        if (this.speaking) {
          clearInterval(this.intervalID);
          this.speaking = false;
          console.log(`forceSpeak: ${forceSpeak}`);
          if (!forceSpeak) {
            return;
          }
        }
      }

      // We say each speech item as its own utterance
      // This gives a nice pause between paragraphs
      this.speaking = true;
      const items = this.getSpeechItems();
      const utterances = items.map(item => this.makeUtterance(item));
      console.log("Made utterances");

      // const lastUtterance = utterances[utterances.length - 1];
      // const lastOnEnd = lastUtterance.onend;
      // lastUtterance.onend = (event) => {
      //   lastOnEnd(event);
      //   this.speaking = false;
      // }
      
      //utterances.forEach((utterance) => synth.speak(utterance));
      utterances.forEach(utterance => {
        console.log(utterance.text);
        synth.speak(utterance);
      });
    },

    triggerAutospeakWithDelay(flag, delay=100) {
      if (flag) {
        setTimeout(() => {
          this.triggerAutospeak();
        }, delay);
      } else if (this.speaking) {
        window.speechSynthesis.cancel();
        this.speaking = false;
      }
    }

  },

  watch: {
    // For the v-dialog slideshows, using nextTick (again, since triggerAutospeak uses it)
    // didn't seem to be enough - the DOM changes hadn't finished propagating yet.
    // But this does the trick, and I don't notice it at all
    autospeakOnChange(_item) {
      this.triggerAutospeakWithDelay(this.speechSettings.autoread);
    },

    speakFlag(flag) {
      this.triggerAutospeakWithDelay(flag);
    }
  }
}
</script>
