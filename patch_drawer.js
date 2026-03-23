const fs = require('fs');
let html = fs.readFileSync('/opt/PersonBlog/static/index.html', 'utf8');

// The CSS fixes:
// Change .modal-comments to NOT animate padding, keep padding 0.
html = html.replace('.modal-comments {', `
        .modal-comments {
            /* INNER WRAPPER PREVENTS TEXT SQUISH */`);

// Wait, I should just use replace_string_in_file via tool.
