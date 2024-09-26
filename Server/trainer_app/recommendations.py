fields = ["clean_speech", "speech_rate", "background_noise", "intelligibility", "clothes",
          "gestures", "angle", "glances", "emotionality", "neutral_emotionality"]
EMOTIONS = ["Happiness", "Anger", "Disgust", "Neutral", "Sadness", "Surprise"]
CONSTANTS = {
    "clean_speech": (0.3, 0.8),
    "speech_rate": (0.3, 0.6),
    "background_noise": (0.3, 0.6),
    "intelligibility": (0.3, 0.6),
    "clothes": (0.5, 1),
    "gestures": (0, 1),
    "angle": (0.3, 0.6),
    "glances": (0.6, 1),
    "emotionality": (0.3, 0.6),
    "neutral_emotionality_official": (0.2, 0.6),
    "neutral_emotionality_nonofficial": (0.2, 0.6),
}
ORDER = [
    "background_noise",
    "speech_rate",
    "emotionality",
    "intelligibility",
    "gestures",
    "glances",
    "angle",
]
OPTIMAL_VALUES = {
    "speech_rate": 0,
    "background_noise": 0,
    "intelligibility": 1,
    "gestures": 1,
    "angle": 0,
    "glances": 0,
    "emotionality": 0
}

UNKNOWN = "Нет информации"
UNKNOWN_ENG = "No information"

STATISTICS_FLAGS = [UNKNOWN, "Низкая", "Средняя", "Высокая"]
STATISTICS_FLAGS_ENG = [UNKNOWN_ENG, "Low", "Average", "High"]
CLOTHES_FLAGS = [UNKNOWN, "Неподходящий", "Подходящий"]
CLOTHES_FLAGS_ENG = [UNKNOWN_ENG, "Unsuitable", "Suitable"]

DRAW_VALUES = {
    "speech_rate": {
        0: "Оптимальный темп речи",
        1: "Немного медленный темп речи",
        2: "Слишком медленный темп речи"
    },
    "background_noise": {
        0: "Нет фонового шума",
        1: "Небольшой фоновый шум",
        2: "Сильный фоновый шум"
    },
    "intelligibility": {
        0: "Речь совсем неразборчива",
        1: "Речь немного неразборчива",
        2: "Речь полностью разборчива",
    },
    "gestures": {
        0: 'Неактивная жестикуляция',
        1: 'Оптимальная жестикуляция',
        2: 'Активная жестикуляция',
    },
    "glances": {
        0: None,
        1: 'Вы часто отводите взгляд'
    },
    "emotionality": {
        0: "Преимущественно желаемые эмоции",
        1: "Не полностью желаемые эмоции",
        2: "Не желаемые эмоции",
    },
    "lightning": {
        0: 'Слишком темное освещение',
        1: 'Оптимальное освещение',
        2: 'Слишком яркое освещение',
    }
}

DRAW_VALUES_ENG = {
    "speech_rate": {
        0: "Optimal speech rate",
        1: "Slightly slow speech rate",
        2: "Speech rate is too slow"
    },
    "background_noise": {
        0: "No background noise",
        1: "Some background noise",
        2: "Strong background noise"
    },
    "intelligibility": {
        0: "Speech is completely unintelligible",
        1: "Speech is a little slurred",
        2: "Speech is completely intelligible",
    },
    "gestures": {
        0: 'Inactive gesticulation',
        1: 'Optimal gesticulation',
        2: 'Active gesticulation',
    },
    "glances": {
        0: None,
        1: 'You often look away'
    },
    "emotionality": {
        0: "Predominantly desired emotions",
        1: "Not completely desired emotions",
        2: "Unwanted emotions",
    },
    "lightning": {
        0: 'Too dark lighting',
        1: 'Optimal lighting',
        2: 'Too bright lighting',
    }
}

RECOMMENDATIONS_TEXTS = {
    "clean_speech": {
        -1: UNKNOWN,
        2: "К сожалению, в Вашей речи слишком много слов-паразитов!\n"
           "Сознательно отслеживайте свою речь и обращайте внимание на использование слов-паразитов. "
           "Постарайтесь выявить наиболее часто используемые слова-паразиты.\n"
           "Планируйте свою речь заранее, делайте небольшие паузы, чтобы подумать о том, как можно было бы "
           "выразить свои мысли более точно и лаконично.\nПостепенно работайте над расширением "
           "своего лексического запаса. Используйте синонимы для избегания повторений одних и тех же слов.",
        1: "У Вас довольно чистая речь, но иногда проскальзывают слова-паразиты.\n"
           "Сознательно отслеживайте свою речь и обращайте внимание на использование слов-паразитов. "
           "Постарайтесь выявить наиболее часто используемые слова-паразиты. "
           "Постепенно работайте над расширением своего лексического запаса",
        0: "У Вас очень грамотная речь! Наличие слов-паразитов минимально.",
    },
    "speech_rate": {
        -1: UNKNOWN,
        0: "У Вас замечательный темп речи! Вы говорите достаточно быстро, не создаете длительных пауз.",
        1: "У Вас довольно низкий темп речи. Попробуйте сознательно увеличить скорость своей речи. "
           "Это можно сделать, постараясь произносить слова чуть быстрее и не останавливаясь на каждом слове."
           "Постарайтесь заранее формулировать, что собираетесь сказать в своем выступлении.",
        2: "У Вас очень медленный темп речи!\n"
           "Попробуйте сознательно увеличить скорость своей речи. "
           "Это можно сделать, постараясь произносить слова чуть быстрее и не останавливаясь на каждом слове."
           "\nПостарайтесь расслабиться и не нервничать перед выступлением. "
           "Часто стресс и нервозность могут делать нашу речь медленной и заикание."
           "Постарайтесь заранее формулировать, что собираетесь сказать в своем выступлении.",
    },
    "background_noise": {
        -1: UNKNOWN,
        0: "В записи практически нет постороннего шума! Вашей речи ничего не мешает.",
        1: "В записи присутствует посторонний шум! Постарайтесь убрать его, чтобы легче было выступать.",
        2: "В записи очень много постороннего шума! Он мешает слушателям воспринимать Вашу речь.",
    },
    "intelligibility": {
        -1: UNKNOWN,
        0: "Ваша речь совсем неразборчива! "
           "Это может быть вызвано слишком быстрым темпом речи,"
           " высоким уровнем фонового шума или тихим голосом. "
           "Постарайтесь четче произносить слова. Уделите внимание правильному произношению слов и звуков,"
           " чтобы ваша речь звучала более четко и разборчиво."
           "\nДайте слушателям возможность усвоить информацию, делая ударения и делая паузы в "
           "ключевых моментах вашего выступления.",
        1: "Ваша речь не очень разборчива. "
           "Это может быть вызвано слишком быстрым темпом речи, высоким уровнем фонового шума "
           "или тихим голосом. Постарайтесь четче произносить слова. Уделите внимание правильному "
           "произношению слов и звуков, чтобы ваша речь звучала более четко и разборчиво.",
        2: "Ваша речь полностью разборчива.",
    },
    "clothes": {
        -1: UNKNOWN,
        0: "К сожалению, Ваша одежда не подходит для формального выступления. "
           "Постарайтесь подбирать более официальную одежду.",
        1: "Вы соблюдаете соответствующий выступлению стиль одежды.",
    },
    "gestures": {
        -1: UNKNOWN,
        0: "Вы полностью неподвижны во время выступления. "
           "Постарайтесь добавить немного артикуляции, "
           "чтобы вести повествование нагляднее и удерживать внимание аудитории.",
        1: "Ваша жестикуляция хорошо подходит для публичного выступления. "
           "Ваши движения помогут привлечь внимание аудитории и наладить с ними контакт.",
        2: "Вы чересчур подвижны и слишком активно жестикулируете во время выступления. "
           "Проконтролируйте скорость и амплитуду движений: cлишком быстрые или чрезмерно "
           "широкие движения могут выглядеть нервозно. Попробуйте замедлить и умерить свои жесты. "
           "Выразительные жесты могут быть эффективны, но они должны быть под контролем.",
    },
    "angle": {
        -1: UNKNOWN,
        0: "Ваш ракурс хорошо подходит для проведения публичных выступлений.",
        1: "Проверьте освещение: обеспечьте хорошее и равномерное освещение в помещении, где вы выступаете. "
           "Избегайте сильных контуров и теней на лице, так как это может делать вас менее видимым."
           "\nРасположите камеру на уровне глаз: Располагая камеру на уровне вашего глаза, "
           "вы создадите более комфортную и натуральную перспективу для аудитории.",
        2: "Проверьте освещение: обеспечьте хорошее и равномерное освещение в помещении, где вы выступаете."
           " Расположите камеру на уровне глаз: Располагая камеру на уровне вашего глаза, "
           "вы создадите более комфортную и натуральную перспективу для аудитории.",

    },
    "glances": {
        -1: UNKNOWN,
        0: "Вы хорошо создаете ощущение прямого контакта и участия.",
        1: "Избегайте избыточного отвода взгляда: Помните, что постоянный отвод взгляда может создать "
           "впечатление дистанции или нервозности. "
           " Используйте технику 'трех секунд': Практикуйте правило 'трех секунд' – держите взгляд на одном"
           " человеке или группе не менее трех секунд, чтобы сделать контакт и убедиться, "
           "что они вас слышат и понимают.",
        2: "Избегайте избыточного отвода взгляда: Помните, что постоянный отвод взгляда может "
           "создать впечатление дистанции или нервозности. Стремитесь держать взгляд на аудитории "
           "большую часть времени, обращаясь к каждому сегменту зала. Используйте технику 'трех секунд': "
           "Практикуйте правило 'трех секунд' – держите взгляд на одном человеке или группе не менее "
           "трех секунд, чтобы сделать контакт и убедиться, что они вас слышат и понимают.",
    },
    "emotionality": {
        -1: UNKNOWN,
        0: "Вы выражаете эмоции, указанные как желаемые. "
           "Вам удается эмоциональная окраска повествования в соответствии с Вашими пожеланиями.",
        1: "Вам не всегда удается выражать эмоции, указанные как желаемые. "
           "Обратите больше внимания на эмоциональную окраску речи.",
        2: "Вы почти не выражаете эмоции, указанные как желаемые. "
           "Обратите больше внимания на эмоциональную окраску речи.",
    },
    "neutral_emotionality": {
        -1: UNKNOWN,
        0: "Вы выступаете совсем безэмоционально.\n"
           "Добавьте эмоций: используйте живость в речи, используйте жесты, интонации, улыбки и "
           "другие эмоциональные средства для того, чтобы подчеркнуть важные моменты и заинтересовать"
           " аудиторию. Покажите свою страсть к теме и поддержите это эмоциями.",
        1: "Вы достаточно эмоциональны для того чтобы привлечь внимание публики и наладить контакт.",
        2: "Вы излишне эмоциональны; это не всегда уместно."
           "\nЗадайте себе цель: gрежде выступления определитесь с основной мыслью или целью, "
           "которую вы хотите донести до аудитории. Это поможет сосредоточиться и не отвлекаться на "
           "излишние эмоции.\nДышите глубоко: Если чувства начинают вас захлестывать, попробуйте сделать "
           "глубокий вдох и медленный выдох. Это поможет вам успокоиться и вернуть контроль над своими эмоциями.",
    },
    "gestures_dynamic": {
        -1: UNKNOWN,
        0: ("Вы полностью неподвижны во время выступления. ", "Это соответствует желаемой жестикуляции.",
            "Для соблюдения неподвижности будьте неподвижны."),
        1: ("У вас средняя активность жестикуляции. ", "Это соответствует желаемой жестикуляции.",
            "Для средней активности будьте средними."),
        2: ("Вы активно жестикулируете во время выступления. ", "Это соответствует желаемой жестикуляции.",
            "Постарайтесь быть активнее."),
    },
}

RECOMMENDATIONS_TEXTS_ENG = {
    "clean_speech": {
        -1: UNKNOWN_ENG,
        2: "Your speech has many filler words! Be more attentive.",
        1: "Your speech is quite clear, but sometimes filler words slip through.",
        0: "Your speech is absolutely clear!",
    },
    "speech_rate": {
        -1: UNKNOWN_ENG,
        0: "Your speech rate is wonderful! You speak quickly enough without creating long pauses.",
        1: "Your speech rate is quite low. "
           "Try to formulate in advance what you are going to say in your speech.",
        2: "Your speech rate is very slow! "
           "Try to prepare a speech plan in advance so as not to get lost and avoid long pauses.",
    },
    "background_noise": {
        -1: UNKNOWN_ENG,
        0: "There is practically no extraneous noise in the recording! Nothing interferes with your speech.",
        1: "There is extraneous noise in the recording! Try to remove it to make performing easier.",
        2: "There is a lot of extraneous noise in the recording! It prevents listeners from perceiving your speech.",
    },
    "intelligibility": {
        -1: UNKNOWN_ENG,
        0: "Your speech is completely unintelligible! "
           "This may be caused by speaking at a fast pace, high levels of background noise, or speaking in a low "
           "voice. Try to work on these factors.",
        1: "Your speech is not very clear. This may be caused by high levels of background noise or a low voice. "
           "Try to work on these factors.",
        2: "Your speech is completely intelligible.",
    },
    "clothes": {
        -1: UNKNOWN_ENG,
        0: "Unfortunately, your clothing is not suitable for a formal presentation. "
           "Try to choose more formal clothes.",
        1: "You maintain a dress code appropriate for the performance.",
    },
    "gestures": {
        -1: UNKNOWN_ENG,
        0: "You are completely motionless during the performance. "
           "Try to add a little articulation to make the story clearer and keep the audience's attention.",
        1: "Your gestures are well suited for public speaking. "
           "Your movements help attract the attention of the audience and establish contact with them.",
        2: "You are too mobile and gesticulate too actively during your speech. Try to be more restrained.",
    },
    "angle": {
        -1: UNKNOWN_ENG,
        0: "Your perspective is well suited for public speaking.",
        1: "Adjust the camera position to achieve a more suitable angle.",
        2: "Pay attention to the even distribution of space around you so as not to cause discomfort to the audience.",
    },
    "glances": {
        -1: UNKNOWN_ENG,
        0: "You are good at creating a sense of direct contact and participation.",
        1: "If you find it difficult to maintain a constant gaze direction towards the camera or audience, "
           "try to move your gaze slowly and smoothly, avoiding jumps and excessive nervousness.",
        2: "Avoid a distracted or aimless direction of gaze, "
           "as this may cause a feeling of uncertainty or immediate disorientation in the audience.",
    },
    "emotionality": {
        -1: UNKNOWN,
        0: "You express the emotions indicated as desired. "
           "You manage to convey the emotional coloring of the narrative in accordance with your wishes.",
        1: "You are not always able to express the emotions indicated as desired. "
           "Pay more attention to the emotional coloring of speech.",
        2: "You hardly express the emotions indicated as desired. "
           "Pay more attention to the emotional coloring of speech.",
    },
    "neutral_emotionality": {
        -1: UNKNOWN_ENG,
        0: "You are overly emotional; this is not always appropriate. Try to be more restrained.",
        1: "You are emotional enough to attract the public's attention and establish contact.",
        2: "You act completely unemotionally. Try to make your story more lively to keep the audience's attention.",
    },
    "gestures_dynamic": {
        -1: UNKNOWN,
        0: ("You are completely motionless during the performance. ", "This corresponds to the desired gesture.",
            "For low gestures be more reserved."),
        1: ("Your gestural activity is average. ", "This corresponds to the desired gesture.",
            "Try to gesture moderately."),
        2: ("You gesticulate actively during your speech. ", "This corresponds to the desired gesture.",
            "Try to be more active during your speech."),
    },
}

LANGUAGE = {
    "Russian": {
        "STATISTICS_FLAGS": STATISTICS_FLAGS,
        "CLOTHES_FLAGS": CLOTHES_FLAGS,
        "DRAW_VALUES": DRAW_VALUES,
        "RECOMMENDATIONS_TEXTS": RECOMMENDATIONS_TEXTS
    },
    "English": {
        "STATISTICS_FLAGS": STATISTICS_FLAGS_ENG,
        "CLOTHES_FLAGS": CLOTHES_FLAGS_ENG,
        "DRAW_VALUES": DRAW_VALUES_ENG,
        "RECOMMENDATIONS_TEXTS": RECOMMENDATIONS_TEXTS_ENG
    }
}
