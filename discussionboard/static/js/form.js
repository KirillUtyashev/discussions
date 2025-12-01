jQuery(document).ready(function ($) {
  initEditor = function (id, removePrev = true) {

    if (removePrev) {
      tinymce.remove(`#${id}`)
    }

    tinymce.init({
      language: 'ru',
      selector: `#${id}`,
      promotion: false,
      toolbar_mode: "sliding",
      plugins: ["advlist", "anchor", "autolink", "charmap", "code", "codesample", "fullscreen",
        "image", "insertdatetime", "link", "lists", "media",
        "preview", "searchreplace", "table", "visualblocks",
      ],
      menubar: "edit view insert format table",
      toolbar: "styles | bold italic underline strikethrough link | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | image | mathjax | codesample",
      external_plugins: {
        'mathjax': '/static/js/math/plugin.min.js'
      },
      image_title: false,
      image_dimensions: false,
      image_description: false,
      file_picker_types: 'image',
      paste_data_images: true,
      file_picker_callback: function (cb, value, meta) {
        let input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'image/*');
        input.click();

        input.onchange = function () {

          let file = this.files[0];
          let filename = "discussii" + Date.now()

          const uploadManager = new Bytescale.UploadManager({
            apiKey: "public_W142ic186BgC8epkuHDt9nKZgytH"
          })

          uploadManager.upload({
            data: file,
            path: {
              folderPath: "/discussions",
            }
          }).then(function (result) {
            url = result.fileUrl.replace("/raw/", "/image/")
            url = url + "?w=1200"
            
            cb(url, {
              title: filename
            })

            setTimeout(function () {
              $(`.tox-dialog__footer .tox-button[title="Сохранить"]`).click()
            }, 100)
          })
        }
      },
      mathjax: {
        lib: '/static/js/math/mathjax/es5/tex-chtml.js',
      }
    });
  }

  window.Prism = window.Prism || {};
  Prism.manual = true;

  renderContent = function () {
    Prism.highlightAll()
    MathJax.typeset()
  }

})