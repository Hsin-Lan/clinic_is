from app import app, db
from models import Patient, Prescription, Drug

def init_database():
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")

        # 添加一些示例数据
        if Drug.query.count() == 0:
            sample_drugs = [
                Drug(name='阿莫西林胶囊', price=15.00, unit='盒', is_common=True),
                Drug(name='布洛芬片', price=12.50, unit='盒', is_common=True),
                Drug(name='感冒灵颗粒', price=18.00, unit='盒', is_common=True),
                Drug(name='维生素C片', price=8.00, unit='瓶', is_common=True),
                Drug(name='头孢克肟分散片', price=25.00, unit='盒', is_common=True),
            ]
            for drug in sample_drugs:
                db.session.add(drug)
            db.session.commit()
            print("示例药品数据添加完成")

        print("数据库初始化完成！")

if __name__ == '__main__':
    init_database()
