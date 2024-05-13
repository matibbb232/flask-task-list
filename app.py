from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, request

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Group: {self.id}>"


class Todo(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Task {self.id}>"


with app.app_context():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def index() -> str:
    groups = Groups.query.order_by(Groups.id).all()
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template("index.html", tasks=tasks, groups=groups)


@app.route("/add_task/<int:group_id>", methods=["POST"])
def add_task(group_id: int) -> str:
    # if request.method == "POST":
    task_content = request.form["content"]

    new_task = Todo(content=task_content, group_id=group_id)

    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        db.session.rollback()
        return "There was an issue when adding your task: " + repr(e)


@app.route("/add_group", methods=["POST"])
def add_group() -> str:
    # if request.method == "POST":
    group_content = request.form["group"]

    new_task = Groups(group=group_content)  # FIXME: some better names?

    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        db.session.rollback()
        return "There was an issue when adding task group: " + repr(e)


@app.route("/delete_group/<int:id>")
def delete_group(id: int) -> str:
    tasks_to_delete = Todo.query.filter(Todo.group_id == id).all()
    group_to_delete = Groups.query.get_or_404(id)

    try:
        for task in tasks_to_delete:
            db.session.delete(task)
        db.session.delete(group_to_delete)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        db.session.rollback()
        return "There was an issue when deleting task: " + repr(e)


@app.route("/delete/<int:id>")
def delete(id: int) -> str:
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        db.session.rollback()
        return "There was an issue when deleting task: " + repr(e)


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id: int) -> str:
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]

        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            return "There was an issue when updating task:" + repr(e)

    return render_template("update.html", task=task)


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()
