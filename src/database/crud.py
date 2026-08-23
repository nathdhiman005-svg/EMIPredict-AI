from sqlalchemy.orm import Session
from .models import FinancialAssessment, ModelPerformance

def create_assessment(db: Session, data: dict):
    assessment = FinancialAssessment(**data)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

def get_assessments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FinancialAssessment).order_by(FinancialAssessment.created_at.desc()).offset(skip).limit(limit).all()

def get_assessments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(FinancialAssessment).filter(FinancialAssessment.user_id == user_id).order_by(FinancialAssessment.created_at.desc()).offset(skip).limit(limit).all()

def get_assessment_by_id(db: Session, assessment_id: int):
    return db.query(FinancialAssessment).filter(FinancialAssessment.id == assessment_id).first()

def update_assessment(db: Session, assessment_id: int, updated_data: dict):
    assessment = get_assessment_by_id(db, assessment_id)
    if not assessment:
        return None
        
    for key, value in updated_data.items():
        if hasattr(assessment, key):
            setattr(assessment, key, value)
            
    db.commit()
    db.refresh(assessment)
    return assessment

def delete_assessment(db: Session, assessment_id: int):
    assessment = get_assessment_by_id(db, assessment_id)
    if assessment:
        db.delete(assessment)
        db.commit()
        return True
    return False

# Model Performance CRUD
def create_model_performance(db: Session, data: dict):
    performance = ModelPerformance(**data)
    db.add(performance)
    db.commit()
    db.refresh(performance)
    return performance

def get_model_performances(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ModelPerformance).order_by(ModelPerformance.created_at.desc()).offset(skip).limit(limit).all()

def get_model_performance_by_id(db: Session, record_id: int):
    return db.query(ModelPerformance).filter(ModelPerformance.id == record_id).first()

def update_model_performance(db: Session, record_id: int, updated_data: dict):
    performance = get_model_performance_by_id(db, record_id)
    if not performance:
        return None
        
    for key, value in updated_data.items():
        if hasattr(performance, key):
            setattr(performance, key, value)
            
    db.commit()
    db.refresh(performance)
    return performance

def delete_model_performance(db: Session, record_id: int):
    performance = get_model_performance_by_id(db, record_id)
    if performance:
        db.delete(performance)
        db.commit()
        return True
    return False
