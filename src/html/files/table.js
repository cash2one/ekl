function create_table(data, table_id) {
    var table = $("#" + table_id);
    // head
    var thead = $("<thead></thead>").appendTo(table);
    var head_str = "<tr>";
    $.each(data.data.header, function(i, item) {
        if (i == 0) {
            head_str += "<th class=\"col-md-5\">" + item + "</th>";
        } else if (i == 1) {
            head_str += "<th class=\"col-md-3\">" + item + "</th>";
        } else if (i == 3) {
            head_str += "<th class=\"col-md-2\">" + item + "</th>";
        } else if (i == 4) {
            head_str += "<th class=\"col-md-2\">" + item + "</th>";
        }
    });
    head_str += "</tr>";
    thead.append(head_str);
    // body
    var tbody = $("<tbody></tbody>").appendTo(table);
    $.each(data.data.content, function(i, line) {
        if (line[2] == 1) {
            body_str = "<tr class=\"success\">";
        } else if (line[2] == 2) {
            body_str = "<tr class=\"danger\">";
        } else if (line[2] == 0) {
            body_str = "<tr>";
        }
        $.each(line, function(j, item) {
            if (j == 3) {
                item = new Date(parseInt(item) * 1000).toLocaleString();
            }
            if (j == 0) {
                body_str += "<td class=\"col-md-5\">" + item + "</td>";
            } else if(j == 1) {
                body_str += "<td class=\"col-md-3\">" + item + "</td>";
            } else if (j == 3) {
                body_str += "<td class=\"col-md-2\">" + item + "</td>";
            } else if (j == 4) {
                body_str += "<td class=\"col-md-2\">" + item + "</td>";
            }
        });
        body_str += "</tr>";
        tbody.append(body_str);
    });
};


function update(data, table_id, index, status) {
    var item = data.data.content[index];
    var word = item[0];
    var cid = item[1];
    var url = "/api/v1/update?word=" + word + "&cid=" + cid + "&st=" + status;
    $.getJSON(url, function(data) {
        var table = $("#" + table_id);
        var tr = table.children("tbody").children("tr:eq(" + index + ")");
        // 根据不同状态码变色
        if (status == 0) {
            tr.removeClass("success");
            tr.removeClass("danger")
        } else if (status == 1) {
            tr.addClass("success");
            tr.removeClass("danger")
        } else if (status == 2) {
            tr.addClass("danger");
            tr.removeClass("success")
        }
    });
};


function add_ctrl(table_id) {
    var table = $("#" + table_id);
    var thead = table.children("thead").children("tr:eq(0)");
    thead.append("<th>控制</th>");
    var tbody = table.children("tbody").children("tr");;
    $.each(tbody, function(i, line) {
        var select_btn = "<button type=\"button\" id=\"select_btn\" class=\"btn btn-success\" index=\"" + i + "\">选定</button>"
        var cancel_btn = "<button type=\"button\" id=\"cancel_btn\" class=\"btn btn-default\" index=\"" + i + "\">取消</button>"
        var delete_btn = "<button type=\"button\" id=\"delete_btn\" class=\"btn btn-danger\" index=\"" + i + "\">删除</button>"
        $(line).append("<td><div class=\"btn-group\" role=\"group\" aria-label=\"...\">" + select_btn + delete_btn + cancel_btn + "</div></td>");
    });
};


function page(page_num, line_num, cid, status) {
    var url = "api/v1/list";
    params = new Array();
    params.push("ln=" + line_num);
    params.push("p=" + page_num);
    if (cid != '') {
        params.push("cid=" + cid);
    }
    if (status != '') {
        params.push("st=" + status);
    }
    if (params.length > 0) {
        url += "?" + params.join("&");
    }
    $.getJSON(url, function(data) {
        $("#words_table").empty();
        create_table(data, "words_table");
        add_ctrl("words_table");
        $("table .btn-default").click(function(){
            var index = parseInt($(this).attr("index"));
            update(data, "words_table", index, 0);
        });
        $("table .btn-success").click(function(){
            var index = parseInt($(this).attr("index"));
            update(data, "words_table", index, 1);
        });
        $("table .btn-danger").click(function(){
            var index = parseInt($(this).attr("index"));
            update(data, "words_table", index, 2);
        });
        if (data.data.content.length == 0) {
            page_num -= 1;
        }
    });
};


function create_pager(cid, status, line_num, page_num, container_id) {
    var url = "api/v1/total";
    var container = $("#" + container_id);
    container.empty();
    params = new Array();
    if (cid != '') {
        params.push("cid=" + cid);
    }
    if (status != '') {
        params.push("st=" + status);
    }
    if (params.length > 0) {
        url += "?" + params.join("&");
    }
    $.getJSON(url, function(data) {
        total = data.data.total;
        total_page = parseInt(total / line_num);
        if (total % line_num > 0) {
            total_page += 1;
        }
        var nav = $("<nav></nav>").appendTo(container);
        var ul = $("<ul class=\"pagination\"></ul>").appendTo(nav);
        for (var i = 0; i < total_page; i++) {
            if (i + 1 == page_num) {
                ul.append("<li class=\"active page_id\"><a href=\"#\">" + (i + 1) + "</a></li>");
            } else {
                ul.append("<li class=\"page_id\"><a href=\"#\">" + (i + 1) + "</a></li>");
            }
        }
        $(".page_id").click(function() {
            var page_id = $(this).text();
            page(page_id, line_num, cid, status);
        });
    });
};
