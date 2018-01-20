<table border=1>
    <tr>
        <th>Title</th>
        <th>Author</th>
        <th>Likes</th>
        <th>Comments</th>
        <th colspan="3">Label</th>
    </tr>
    %for row in rows:
    %if row.label=="good":
        <tr bgcolor=#71E480>
            <td><a href={{row.url}}>{{row.title}}</a></td>
            <td>{{row.author}}</td>
            <td>{{row.points}}</td>
            <td>{{row.comments}}</td>
            <td><a href="/add_label/?label=good&id={{row.id}}">Интересно</a></td>
            <td><a href="/add_label/?label=maybe&id={{row.id}}">Возможно</a></td>
            <td><a href="/add_label/?label=never&id={{row.id}}">Не интересно</a></td>
        </tr>
    %end
    %if row.label=="maybe":
        <tr bgcolor=#FAF683>
            <td><a href={{row.url}}>{{row.title}}</a></td>
            <td>{{row.author}}</td>
            <td>{{row.points}}</td>
            <td>{{row.comments}}</td>
            <td><a href="/add_label/?label=good&id={{row.id}}">Интересно</a></td>
            <td><a href="/add_label/?label=maybe&id={{row.id}}">Возможно</a></td>
            <td><a href="/add_label/?label=never&id={{row.id}}">Не интересно</a></td>
        </tr>
    %end
    %if row.label=="never":
        <tr bgcolor=#EF5B3D>
            <td><a href={{row.url}}>{{row.title}}</a></td>
            <td>{{row.author}}</td>
            <td>{{row.points}}</td>
            <td>{{row.comments}}</td>
            <td><a href="/add_label/?label=good&id={{row.id}}">Интересно</a></td>
            <td><a href="/add_label/?label=maybe&id={{row.id}}">Возможно</a></td>
            <td><a href="/add_label/?label=never&id={{row.id}}">Не интересно</a></td>
        </tr>
    %end
    %end
</table>
<a href="/update_news">I Wanna more HACKER NEWS!</a>